"""
Chat service for Uzhathunai v2.0.
"""
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from app.models.chat import ChatChannel, ChatChannelMember, ChatMessage
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.enums import ChatContextType, MessageType, MemberStatus
from app.schemas.chat import ChatChannelCreate, ChatMessageCreate
from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, PermissionError, ValidationError

logger = get_logger(__name__)


class ChatService:
    """Service for In-App Chat."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
        
    def create_channel(
        self,
        user_id: UUID,  # Creator
        data: ChatChannelCreate,
        participant_org_ids: List[UUID]
    ) -> ChatChannel:
        """
        Create a new chat channel and add participants.
        Ensure one channel per context (e.g. WorkOrder) usually.
        """
        # Validate User is member of one of the participant orgs with proper role?
        # For WorkOrder context, usually initiated by FSP or Farmer.
        
        # Check if channel already exists for this context
        existing = self.db.query(ChatChannel).filter(
            ChatChannel.context_type == data.context_type,
            ChatChannel.context_id == data.context_id
        ).first()
        
        if existing:
            # Check if members actually exist, if not, add them (self-healing for broken channels)
            existing_count = self.db.query(ChatChannelMember).filter(
                ChatChannelMember.channel_id == existing.id
            ).count()
            
            if existing_count == 0 and participant_org_ids:
                logger.info(f"Backfilling missing members for existing channel {existing.id}: {participant_org_ids}")
                for org_id in participant_org_ids:
                    member = ChatChannelMember(
                        channel_id=existing.id,
                        organization_id=org_id,
                        added_by=user_id
                    )
                    self.db.add(member)
                self.db.commit()
                
            return existing
            
        # Create Channel
        channel = ChatChannel(
            context_type=data.context_type,
            context_id=data.context_id,
            name=data.name,
            created_by=user_id,
            updated_by=user_id,
            updated_at=datetime.utcnow()
        )
        self.db.add(channel)
        self.db.flush()
        
        # Add Members
        logger.info(f"DEBUG: Adding members to channel {channel.id}: {participant_org_ids}")
        for org_id in participant_org_ids:
            member = ChatChannelMember(
                channel_id=channel.id,
                organization_id=org_id,
                added_by=user_id
            )
            self.db.add(member)
            
        self.db.commit()
        self.db.refresh(channel)
        return channel

    def get_user_channels(
        self,
        user_id: UUID,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[ChatChannel], int]:
        """
        Get channels for a user based on their organization memberships.
        """
        # 1. Get user's active organizations
        user_orgs = self.db.query(OrgMember.organization_id).filter(
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).subquery()
        
        # 2. Find channels where these organizations are members
        query = self.db.query(ChatChannel).join(
            ChatChannelMember,
            ChatChannel.members
        ).filter(
            ChatChannelMember.organization_id.in_(user_orgs),
            ChatChannel.is_active == True
        ).distinct()
        
        total = query.count()
        
        channels = query.order_by(
            ChatChannel.updated_at.desc()
        ).offset((page - 1) * limit).limit(limit).all()
        
        return channels, total

    def send_message(
        self,
        channel_id: UUID,
        user_id: UUID,
        data: ChatMessageCreate
    ) -> ChatMessage:
        """
        Send a message to a channel.
        verify user is part of an organization that is a member of the channel.
        """
        # Verify Channel exists
        channel = self.db.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
        if not channel:
            raise NotFoundError("Channel not found", "CHANNEL_NOT_FOUND")
            
        # Identify User's Org in this channel
        # User must be an active member of an Org that is a member of this Channel
        user_org = self.db.query(Organization).join(
            OrgMember, Organization.id == OrgMember.organization_id
        ).join(
            ChatChannelMember, Organization.id == ChatChannelMember.organization_id
        ).filter(
            ChatChannelMember.channel_id == channel_id,
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        if not user_org:
            raise PermissionError("User is not a member of this chat channel", "PERMISSION_DENIED")
            
        # Create Message
        msg = ChatMessage(
            channel_id=channel_id,
            sender_id=user_id,
            sender_org_id=user_org.id,
            message_type=data.message_type,
            content=data.content,
            media_url=data.media_url
        )
        self.db.add(msg)
        
        # Update Channel timestamp
        channel.updated_at = msg.created_at
        channel.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def repair_channel_membership(self, channel_id: UUID, user_id: UUID) -> bool:
        """
        Attempt to repair a broken channel by backfilling members based on context.
        Returns True if repair was attempted and might have succeeded.
        """
        try:
            channel = self.db.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
            if not channel:
                logger.error(f"[REPAIR] Channel {channel_id} not found.")
                return False
                
            logger.info(f"[REPAIR] Attempting to repair channel {channel.id}. Context: {channel.context_type} ID: {channel.context_id}")
            
            # Only repair if it has NO members (or maybe just missing this user's org?)
            # Let's be aggressive: if this user is denied, check if they SHOULD be in.
            
            # Resolve Context
            if channel.context_type == ChatContextType.WORK_ORDER:
                from app.models.work_order import WorkOrder
                wo = self.db.query(WorkOrder).filter(WorkOrder.id == channel.context_id).first()
                if wo:
                    org_ids = [wo.farming_organization_id, wo.fsp_organization_id]
                    logger.info(f"[REPAIR] Found WorkOrder {wo.id}. Backfilling Orgs: {org_ids}")
                    
                    # Track what we are adding in this transaction to avoid dups
                    added_in_tx = set()
                    
                    added_any = False
                    for org_id in org_ids:
                        if org_id in added_in_tx:
                            continue

                        member_exists = self.db.query(ChatChannelMember).filter(
                            ChatChannelMember.channel_id == channel.id,
                            ChatChannelMember.organization_id == org_id
                        ).first()
                        
                        if not member_exists:
                            logger.info(f"[REPAIR] Adding Org {org_id} to Channel.")
                            member = ChatChannelMember(
                                channel_id=channel.id,
                                organization_id=org_id,
                                added_by=user_id
                            )
                            self.db.add(member)
                            added_in_tx.add(org_id)
                            added_any = True
                    
                    if added_any:
                        self.db.commit()
                        return True
                    else:
                        logger.info(f"[REPAIR] All required orgs are already members.")
                else:
                    logger.error(f"[REPAIR] WorkOrder {channel.context_id} NOT FOUND.")
                    
            elif channel.context_type == ChatContextType.ORGANIZATION:
                 # Context ID is the Target Org ID
                 target_org_id = channel.context_id
                 logger.info(f"[REPAIR] Handling ORGANIZATION context. Target Org: {target_org_id}")
                 
                 added_in_tx = set()
                 added_any = False
                 
                 # 1. Add Target Org (The Provider)
                 target_exists = self.db.query(ChatChannelMember).filter(
                     ChatChannelMember.channel_id == channel.id,
                     ChatChannelMember.organization_id == target_org_id
                 ).first()
                 
                 if not target_exists:
                     logger.info(f"[REPAIR] Adding Target Org {target_org_id}")
                     member = ChatChannelMember(
                         channel_id=channel.id,
                         organization_id=target_org_id,
                         added_by=user_id
                     )
                     self.db.add(member)
                     added_in_tx.add(target_org_id)
                     added_any = True

                 # 2. Add Requesting User's Active Org (The Customer/Farmer)
                 # Find user's active orgs
                 user_orgs = self.db.query(OrgMember).filter(
                     OrgMember.user_id == user_id,
                     OrgMember.status == MemberStatus.ACTIVE
                 ).all()
                 
                 if not user_orgs:
                     logger.warning(f"[REPAIR] User {user_id} has no active organizations.")
                 
                 for u_org in user_orgs:
                     # Check if we already added this org in this transaction
                     if u_org.organization_id in added_in_tx:
                         continue

                     u_exists = self.db.query(ChatChannelMember).filter(
                         ChatChannelMember.channel_id == channel.id,
                         ChatChannelMember.organization_id == u_org.organization_id
                     ).first()
                     
                     if not u_exists:
                         logger.info(f"[REPAIR] Adding User's Org {u_org.organization_id}")
                         u_member = ChatChannelMember(
                             channel_id=channel.id,
                             organization_id=u_org.organization_id,
                             added_by=user_id
                         )
                         self.db.add(u_member)
                         added_in_tx.add(u_org.organization_id)
                         added_any = True
                 
                 if added_any:
                     self.db.commit()
                     return True
            
            else:
                 logger.warning(f"[REPAIR] Unhandled context type: {channel.context_type}")

        except Exception as e:
            logger.error(f"[REPAIR] Failed to repair channel {channel_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
        return False

    def get_messages(
        self,
        channel_id: UUID,
        user_id: UUID,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[ChatMessage], int]:
        """
        Get messages for a channel.
        """
        # logger.info(f"DEBUG: Checking access for user {user_id} to channel {channel_id}")
        
        # Helper debugging - commented out to reduce noise unless needed
        # user_memberships = self.db.query(OrgMember).filter(OrgMember.user_id == user_id).all()
        # logger.info(f"DEBUG: User memberships: {[(m.organization_id, m.status) for m in user_memberships]}")
        
        # channel_members = self.db.query(ChatChannelMember).filter(ChatChannelMember.channel_id == channel_id).all()
        # logger.info(f"DEBUG: Channel members: {[(m.organization_id) for m in channel_members]}")

        # Validate Access
        has_access = self.db.query(ChatChannelMember).join(
            OrgMember, ChatChannelMember.organization_id == OrgMember.organization_id
        ).filter(
            ChatChannelMember.channel_id == channel_id,
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        if not has_access:
            logger.warning(f"access_control: Access denied for {user_id} to {channel_id}. Triggering repair.")
            
            # --- SELF HEALING START ---
            if self.repair_channel_membership(channel_id, user_id):
                # Retry access check
                has_access_retry = self.db.query(ChatChannelMember).join(
                    OrgMember, ChatChannelMember.organization_id == OrgMember.organization_id
                ).filter(
                    ChatChannelMember.channel_id == channel_id,
                    OrgMember.user_id == user_id,
                    OrgMember.status == MemberStatus.ACTIVE
                ).first()
                
                if has_access_retry:
                    logger.info(f"access_control: Repair successful. Access granted.")
                else:
                    logger.error(f"access_control: Repair executed but access still denied. Check User-Org link.")
                    raise PermissionError("Access denied - User not in Member Orgs", "PERMISSION_DENIED")
            else:
                logger.error(f"access_control: Repair failed or not applicable.")
                raise PermissionError("Access denied", "PERMISSION_DENIED")
            # --- SELF HEALING END ---
            
        query = self.db.query(ChatMessage).filter(
            ChatMessage.channel_id == channel_id
        )
        
        total = query.count()
        
        messages = query.order_by(
            desc(ChatMessage.created_at)
        ).offset((page - 1) * limit).limit(limit).all()
        
        return messages, total
