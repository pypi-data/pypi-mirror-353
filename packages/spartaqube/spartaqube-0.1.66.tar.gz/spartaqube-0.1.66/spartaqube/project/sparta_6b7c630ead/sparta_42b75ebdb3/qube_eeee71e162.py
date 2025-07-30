import hashlib
from datetime import datetime
from project.models import UserProfile, UserGroup, UserGroupUser, notificationGroup
from project.logger_config import logger


def sparta_d8af54b558(json_data, user_obj, group_id=None):
    """
    Create a group (to share dataQuantDB, spartBtn or Dashboard)
    """
    groupName = json_data['groupName']
    membersArr = json_data['membersArr']
    dateCreation = datetime.now()
    if group_id is None:
        group_id = hashlib.sha256((str(user_obj.id) + '_' + str(groupName.lower()) + '_' + str(datetime.now())).encode('utf-8')).hexdigest()
    user_group_obj = UserGroup.objects.create(name=groupName, group_id=
        group_id, user_creator=user_obj, date_created=dateCreation,
        last_update=dateCreation)
    UserGroupUser.objects.create(user_group=user_group_obj, user=user_obj,
        b_admin=True, date_created=dateCreation, last_update=dateCreation)
    sparta_05ad5c8714(membersArr, user_group_obj, dateCreation, user_obj)
    res = {'res': 1, 'groupId': group_id}
    return res


def sparta_05ad5c8714(membersArr, user_group_obj, dateCreation, userMe):
    """
        Add members to group and send notifications
    """
    UserGroupUserSet = UserGroupUser.objects.filter(is_delete=0, user_group
        =user_group_obj).all()
    allCurrentUsersOfGroup = [thisObj.user.email for thisObj in
        UserGroupUserSet]
    for thisMember in membersArr:
        thisUserId = thisMember['member']
        group_user_id = hashlib.sha256((str(thisUserId) + '_' + str(
            user_group_obj.name.lower()) + '_' + str(datetime.now())).encode('utf-8')).hexdigest()
        thisUserProfileObj = UserProfile.objects.get(userId=thisUserId)
        if thisUserProfileObj is not None:
            thisuser_obj = thisUserProfileObj.user
            if thisuser_obj.email not in allCurrentUsersOfGroup:
                UserGroupUser.objects.create(user_group=user_group_obj,
                    group_user_id=group_user_id, user=thisuser_obj,
                    date_created=dateCreation, last_update=dateCreation)
                notificationGroup.objects.create(userFrom=userMe, user=
                    thisuser_obj, date_created=dateCreation)
            else:
                logger.debug('member already in group')


def sparta_89bffe37b8(user_obj):
    """
    Returns all the group where i'm a member (admin or not)
    """
    adminGroups = UserGroupUser.objects.filter(is_delete=0, user=user_obj,
        b_admin=True, user_group__is_delete=0).all()
    nonAdminGroups = UserGroupUser.objects.filter(is_delete=0, user=
        user_obj, b_admin=False, user_group__is_delete=0).all()
    allGroups = {'admin': adminGroups, 'nonAdmin': nonAdminGroups}
    return allGroups


def sparta_325a9ff1bc(user_obj):
    """
    Returns all the group where i'm a member (admin or not)
    """
    return UserGroupUser.objects.filter(is_delete=0, user=user_obj,
        user_group__is_delete=0)


def sparta_8863e846b0(json_data, user_obj):
    """
    Returns all the group where i'm a member (admin or not)
    """
    allGroups = sparta_89bffe37b8(user_obj)
    allGroupsAdmin = [{'groupId': thisObj.user_group.groupId, 'name':
        thisObj.user_group.name} for thisObj in allGroups['admin']]
    allGroupsNonAdmin = [{'groupId': thisObj.user_group.groupId, 'name':
        thisObj.user_group.name} for thisObj in allGroups['nonAdmin']]
    return {'res': 1, 'admin': allGroupsAdmin, 'nonAdmin': allGroupsNonAdmin}


def sparta_2f74bfe887(json_data, user_obj):
    """
        Get the list of members for a group (only an admin can run this function)
    """
    thisGroupId = str(json_data['groupId'])
    user_groupSet = UserGroup.objects.filter(is_delete=0, groupId=thisGroupId
        ).all()
    if user_groupSet.count() > 0:
        thisuser_group_obj = user_groupSet[0]
        UserGroupUserSet = UserGroupUser.objects.filter(is_delete=0,
            user_group=thisuser_group_obj, user=user_obj, b_admin=True)
        if UserGroupUserSet.count() > 0:
            UserGroupUserSet = UserGroupUser.objects.filter(is_delete=0,
                user_group=thisuser_group_obj)
            membersArrDict = [{'name': thisObj.user.first_name + ' ' + str(
                thisObj.user.last_name), 'group_user_id': thisObj.group_user_id, 'b_admin': thisObj.b_admin} for thisObj in
                UserGroupUserSet if thisObj.user.email != user_obj.email]
            resDict = {'res': 1, 'membersArrDict': membersArrDict}
            return resDict
    resDict = {'res': -1}
    return resDict


def sparta_7b51624be0(json_data, user_obj):
    """
    Edit group (name, or add member)
    """
    groupId = json_data['groupId']
    groupName = json_data['groupName']
    membersArr = json_data['membersArr']
    user_groupSet = UserGroup.objects.filter(is_delete=0, groupId=groupId).all(
        )
    if user_groupSet.count() > 0:
        thisuser_group_obj = user_groupSet[0]
        UserGroupuser_obj = UserGroupUser.objects.filter(is_delete=0,
            user_group=thisuser_group_obj, user=user_obj, b_admin=True).all()
        if UserGroupuser_obj.count() > 0:
            thisuser_group_obj.name = groupName
            thisuser_group_obj.save()
            dateCreation = datetime.now()
            sparta_05ad5c8714(membersArr, thisuser_group_obj, dateCreation,
                user_obj)
    resDict = {'res': 1}
    return resDict


def sparta_3a80529c20(json_data, user_obj):
    """
    Edit group (name, or add member)
    """
    group_user_id = json_data['group_user_id']
    b_admin = int(json_data['b_admin'])
    UserGroupUserSet = UserGroupUser.objects.filter(is_delete=0,
        group_user_id=group_user_id).all()
    if UserGroupUserSet.count() > 0:
        UserGroupuser_obj = UserGroupUserSet[0]
        if b_admin == 1:
            thisuser_group_obj = UserGroupuser_obj.user_group
            UserGroupUserSet = UserGroupUser.objects.filter(is_delete=0,
                user_group=thisuser_group_obj, user=user_obj, b_admin=True
                ).all()
            if UserGroupUserSet.count() > 0:
                UserGroupuser_obj.b_admin = True
                UserGroupuser_obj.save()
        else:
            thisuser_group_obj = UserGroupuser_obj.user_group
            thisuser_group_objCreator = thisuser_group_obj.user_creator
            if user_obj.email == thisuser_group_objCreator.email:
                UserGroupuser_obj.b_admin = False
                UserGroupuser_obj.save()
    resDict = {'res': 1}
    return resDict


def sparta_d990fee613(json_data, user_obj):
    """
    Edit group (name, or add member)
    """
    groupId = json_data['groupId']
    user_groupSet = UserGroup.objects.filter(is_delete=0, groupId=groupId,
        user_creator=user_obj).all()
    if user_groupSet.count() > 0:
        thisuser_group_obj = user_groupSet[0]
        thisuser_group_obj.is_delete = 1
        thisuser_group_obj.save()
    resDict = {'res': 1}
    return resDict


def sparta_8e388bdc0e(json_data, user_obj):
    """
    Delete a member from the group
    """
    group_user_id = json_data['group_user_id']
    UserGroupUserSet = UserGroupUser.objects.filter(is_delete=0,
        group_user_id=group_user_id).all()
    if UserGroupUserSet.count() > 0:
        UserGroupuser_obj = UserGroupUserSet[0]
        userToDeleteIsAdmin = UserGroupuser_obj.b_admin
        if not userToDeleteIsAdmin:
            thisuser_group_obj = UserGroupuser_obj.user_group
            UserGroupUserSet = UserGroupUser.objects.filter(is_delete=0,
                user_group=thisuser_group_obj, user=user_obj, b_admin=True
                ).all()
            if UserGroupUserSet.count() > 0:
                UserGroupuser_obj.is_delete = 1
                UserGroupuser_obj.save()
        else:
            thisuser_group_obj = UserGroupuser_obj.user_group
            thisuser_group_objCreator = thisuser_group_obj.user_creator
            if user_obj.email == thisuser_group_objCreator.email:
                UserGroupuser_obj.is_delete = 1
                UserGroupuser_obj.save()
    resDict = {'res': 1}
    return resDict


def sparta_c50cec8b4a(json_data, user_obj):
    """
    Leave a group (I am not admin of this group, a simple member who do not want to stay in the group anymore)
    """
    groupId = json_data['groupId']
    user_groupSet = UserGroup.objects.filter(is_delete=0, groupId=groupId).all(
        )
    if user_groupSet.count() > 0:
        thisGroupObj = user_groupSet[0]
        UserGroupUserSet = UserGroupUser.objects.filter(is_delete=0,
            user_group=thisGroupObj, user=user_obj, b_admin=False).all()
        if UserGroupUserSet.count() > 0:
            thisUseGroupuser_obj = UserGroupUserSet[0]
            thisUseGroupuser_obj.is_delete = 1
            thisUseGroupuser_obj.save()
    resDict = {'res': 1}
    return resDict

#END OF QUBE
