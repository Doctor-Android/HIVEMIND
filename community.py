class Community:
    def __init__(self, name, description, creator):
        self.name = name
        self.description = description
        self.creator = creator
        self.spaces = {}
        self.members = {creator: "admin"}
        self.privacy_settings = {
            "visibility": "private",
            "invite_required": True
        }
        self.events = []  # List to store community events
        self.is_public = False  # Track if the community is public
        self.banned_websites = set()
        self.banned_words = set()
        self.rules = []  # List to store community rules
        self.roles = {"admin": set(), "moderator": set(), "member": set()}  # Role management
        self.roles["admin"].add(creator)

    def create_space(self, space_name, description):
        # Create a new space within the community
        if space_name not in self.spaces:
            self.spaces[space_name] = {
                "description": description,
                "members": {self.creator: "admin"}
            }
            print(f"Space '{space_name}' created in community '{self.name}'.")
        else:
            print(f"Space '{space_name}' already exists.")

    def manage_space(self, space_name, action, user=None, role=None):
        if space_name in self.spaces:
            if action == "add_member" and user:
                self.spaces[space_name]["members"][user] = role or "member"
                print(f"User '{user}' added to space '{space_name}' with role '{role or 'member'}'.")
            elif action == "remove_member" and user:
                self.spaces[space_name]["members"].pop(user, None)
                print(f"User '{user}' removed from space '{space_name}'.")
            elif action == "assign_role" and user and role:
                if user in self.spaces[space_name]["members"]:
                    self.spaces[space_name]["members"][user] = role
                    print(f"User '{user}' assigned role '{role}' in space '{space_name}'.")
                else:
                    print(f"User '{user}' is not a member of space '{space_name}'.")
            else:
                print(f"Invalid action or user not specified for space '{space_name}'.")
        else:
            print(f"Space '{space_name}' does not exist.")

    def add_member(self, user, role="member"):
        if self.privacy_settings["invite_required"]:
            print(f"Invite required to join community '{self.name}'.")
        else:
            self.members[user] = role
            print(f"User '{user}' added to community '{self.name}' with role '{role}'.")

    def remove_member(self, user):
        if user in self.members:
            del self.members[user]
            for space in self.spaces.values():
                space["members"].pop(user, None)
            print(f"User '{user}' removed from community '{self.name}'.")
        else:
            print(f"User '{user}' is not a member of community '{self.name}'.")

    def set_privacy_settings(self, visibility=None, invite_required=None):
        if visibility:
            self.privacy_settings["visibility"] = visibility
        if invite_required is not None:
            self.privacy_settings["invite_required"] = invite_required
        print(f"Privacy settings updated for community '{self.name}'.")

    def is_admin(self, user):
        return user in self.roles["admin"]

    def ban_website(self, user, website):
        if self.is_admin(user):
            self.banned_websites.add(website)
            print(f"Website {website} banned by {user}.")
        else:
            print(f"User {user} is not authorized to ban websites.")