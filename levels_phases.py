from all_sprites_and_groups import *


class Level:
    """
    A level class that player should clear.

    Each level has 5 phases.

    Phase 1, 2, 3: normal, Phase 4: challenge, Phase 5: boss

    Each normal phases has score requirements.
    Player can go to next phase only if player got required score.

    Challenge phase gives player a mission.
    It can be a time attack, defeating a specific kind of enemies, etc.
    If player succeeds, then go to the boss phase.
    If player fails, then go back to the first phase.

    In boss phase, player should fight with a boss sprite, hard to defeat.
    If player succeeds, then go to the next level, starting from phase 1 again.
    """

    def __init__(self):
        self.all_phases = []        # List of all phases
        self.phase_count = 0        # Number of phases
        self.current_phase = None   # Current phase playing
        self.boss_phase = None      # Attribute for boss phase
        self.phase_num = 1          # Current phase number

        # Score attribute of current playing phase, needs for displaying phase progress bar
        self.current_phase_required_score = 0
        self.current_phase_score = 0

        self.frames_to_clear = 0    # Measured time to clear this level in frame counts
        self.time_to_clear = 0      # Measured time to clear this level in real time
        self.cleared = False        # Boolean attribute for clearing level

        # For calculating time average score (points/sec)
        self.start_score = 0            # Player's score when starting this level
        self.score = 0                  # Score got in this level
        self.time_average_score = 0

    def add_phase(self, phase):
        """
        Add new phase to this level
        :param phase: new phase to add
        :return: None
        """

        self.all_phases.append(phase)   # Add new phase
        self.phase_count += 1           # Count total phases

    def initialize_level(self):
        """
        Initialize level before starting
        :return: None
        """

        # Set current phase to the first phase and initialize it
        self.phase_num = 1
        self.current_phase = self.all_phases[self.phase_num - 1]
        self.current_phase.initialize_phase()

        # Reset cleared time and status of this level
        self.frames_to_clear = 0
        self.time_to_clear = 0
        self.cleared = False

        # Reset score attributes
        self.current_phase_required_score = self.current_phase.required_score
        self.start_score = player_score[0]
        self.score = 0
        self.time_average_score = 0

    def update(self):
        """
        Update current phase or transition to next phase if necessary
        :return: None
        """

        # Update current phase
        self.current_phase.update()

        # Update current phase's score
        # At boss phase, phase progress bar is always full
        if isinstance(self.current_phase, BossPhase):
            self.current_phase_required_score = self.current_phase_score = 1
        else:
            self.current_phase_required_score = self.current_phase.required_score
            self.current_phase_score = self.current_phase.current_score

        # If current phase is cleared
        if self.current_phase.is_cleared():
            # If this phase is the last phase
            if self.phase_num == self.phase_count:
                self.cleared = True     # Level clear
            else:
                # Go to the next phase and initialize it
                self.current_phase = self.all_phases[self.phase_num]
                self.current_phase.initialize_phase()
                self.phase_num += 1

        # Update playtime
        self.frames_to_clear += 1
        self.time_to_clear = self.frames_to_clear / FPS

        # Update current score
        self.score = player_score[0] - self.start_score
        self.time_average_score = self.score / self.time_to_clear

    def is_cleared(self):
        """
        To check whether this level is cleared
        :return: is this level cleared?
        """

        return self.cleared


class NormalPhase:
    """
    Normal phase which is the 1st, 2nd, 3rd phase of each level.
    Player should fulfill score requirements to go to the next phase.
    """

    def __init__(self, required_score, enemy_count_dict):
        self.required_score = required_score    # Score requirement to clear this phase
        self.current_score = 0                  # Current score to compare with requirement
        self.score_offset = 0                   # not to consider score from other phases or levels

        self.frames_to_clear = 0                # Measured time to clear this phase in frame counts
        self.elapsed_time = 0                   # Currently passed time from start (in seconds)
        self.cleared = False                    # Boolean attribute for clearing phase

        # Set the type of enemies and their count
        self.enemy_type = enemy_count_dict["enemy_type"]    # List of enemy classes
        self.enemy_count = enemy_count_dict["enemy_count"]  # List of enemy counts
        self.num_enemy_kinds = len(self.enemy_type)

    def initialize_phase(self):
        """
        Initialize phase before starting
        :return: None
        """

        # Get current total score before starting
        self.score_offset = player_score[0]
        self.current_score = 0

        # Reset cleared status of this level
        self.frames_to_clear = 0
        self.cleared = False

    def update(self):
        """
        Update current phase
        :return: None
        """

        # Generate enemies of given types and count
        for e in range(self.num_enemy_kinds):
            if len(self.enemy_type[e].group) < self.enemy_count[e]:
                self.enemy_type[e]()

        # Update current score got in this phase
        self.current_score = player_score[0] - self.score_offset

        # Calculate elapsed playtime
        self.frames_to_clear += 1
        self.elapsed_time = self.frames_to_clear / FPS

        # If score requirement is fulfilled
        if self.current_score >= self.required_score:
            self.cleared = True         # Phase clear

    def is_cleared(self):
        """
        To check whether this phase is cleared
        :return: is this phase cleared?
        """

        return self.cleared


class BossPhase:
    """
    The last phase of each level.
    Player should defeat boss of the level.
    """

    def __init__(self, boss_class, enemy_count_dict):
        self.current_score = 0      # Current score to compare with requirement
        self.score_offset = 0       # not to consider score from other phases or levels

        self.frames_to_clear = 0                # Measured time to clear this phase in frame counts
        self.elapsed_time = 0                   # Currently passed time from start (in seconds)
        self.cleared = False                    # Boolean attribute for clearing phase

        # Set the type of enemies and their count
        self.enemy_type = enemy_count_dict["enemy_type"]    # List of enemy classes
        self.enemy_count = enemy_count_dict["enemy_count"]  # List of enemy counts
        self.num_enemy_kinds = len(self.enemy_type)

        # Set boss class and instance
        self.boss_class = boss_class
        self.boss = None

    def initialize_phase(self):
        """
        Initialize phase before starting
        :return: None
        """

        # Get current total score before starting
        self.score_offset = player_score[0]
        self.current_score = 0

        # Reset cleared status of this level
        self.frames_to_clear = 0
        self.cleared = False

        # Generate boss
        self.boss = self.boss_class()

    def update(self):
        """
        Update current phase
        :return: None
        """

        # Generate enemies of given types and count
        for e in range(self.num_enemy_kinds):
            if len(self.enemy_type[e].group) < self.enemy_count[e]:
                self.enemy_type[e]()

        # Update current score got in this phase
        self.current_score = player_score[0] - self.score_offset

        # Calculate elapsed playtime
        self.frames_to_clear += 1
        self.elapsed_time = self.frames_to_clear / FPS

        # If boss is killed by player
        if self.boss and not self.boss.alive():
            self.boss = None
            self.cleared = True         # Phase clear

    def is_cleared(self):
        """
        To check whether this phase is cleared
        :return: is this phase cleared?
        """

        return self.cleared


all_levels = []         # List of all levels

# Define level 1
level_1 = Level()

level_1.add_phase(NormalPhase(required_score=300,           # Phase 1
                              enemy_count_dict={"enemy_type": [StraightLineMover1],
                                                "enemy_count": [120]}))
"""
level_1.add_phase(NormalPhase(required_score=3000000,           # Phase 1
                              enemy_count_dict={"enemy_type": [Wall2],
                                                "enemy_count": [300]}))
"""
level_1.add_phase(NormalPhase(required_score=600,           # Phase 2
                              enemy_count_dict={"enemy_type": [StraightLineMover1,
                                                               StraightLineMover2],
                                                "enemy_count": [160, 40]}))
level_1.add_phase(NormalPhase(required_score=1500,          # Phase 3
                              enemy_count_dict={"enemy_type": [StraightLineMover1,
                                                               StraightLineMover2,
                                                               StraightLineMover3],
                                                "enemy_count": [200, 70, 30]}))
level_1.add_phase(BossPhase(boss_class=BossLV1,             # Phase 5 (boss)
                            enemy_count_dict={"enemy_type": [StraightLineMover1,
                                                             StraightLineMover2,
                                                             StraightLineMover3],
                                              "enemy_count": [200, 70, 30]}))
all_levels.append(level_1)
