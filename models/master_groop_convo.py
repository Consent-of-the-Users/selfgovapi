from models.groop_convo import GroopConvo


class MasterGroopConvo(GroopConvo):
    """The main, always-on conversation for a group, linked to its members."""

    __mapper_args__ = {"polymorphic_identity": "master_groop_convo"}

    participants = None

    @property
    def participants(self):
        """Participants are always the group members."""
        return self.groop.members

    @property
    def title(self):
        """Ensure the title is always fixed to the group's handle."""
        return f"Master Convo for @{self.groop.handle}"

    @participants.setter
    def participants(self, value):
        """Prevent modifying participants directly."""
        raise AttributeError("Cannot modify participants of MasterGroopConvo directly.")

    @title.setter
    def title(self, value):
        """Prevent modifying title manually."""
        raise AttributeError("Cannot modify the title of a MasterGroopConvo.")
