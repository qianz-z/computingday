
def get_group(context):
    group_name = context.user_data['group_name']
    group = context.bot_data['groups'][group_name]
    return group

