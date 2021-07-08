from all_sprites_and_groups import *


class Level:
    def __init__(self):
        self.all_phases = []
        self.phase_count = 0
        self.current_phase = None
        self.boss_phase = None
        self.phase_num = 0

        self.frames_to_clear = 0
        self.cleared = False

        self.initialize_level()

    def add_phase(self, phase):
        self.all_phases.append(phase)
        self.phase_count += 1

    def initialize_level(self):
        for phase in self.all_phases:
            phase.initialize_phase()

        self.phase_num = 0
        self.current_phase = self.all_phases[self.phase_num]

    def update(self):
        self.current_phase.update()
        if self.current_phase.is_cleared():
            self.phase_num += 1
            if self.phase_num < self.phase_count:
                self.current_phase = self.all_phases[self.phase_num]
            else:
                self.cleared = True


class NormalPhase:
    def __init__(self, required_score, enemy_count_dict):
        self.required_score = required_score
        self.current_score = 0
        self.score_offset = 0

        self.frames_to_clear = 0
        self.elapsed_time = 0
        self.cleared = False

        self.enemy_type = enemy_count_dict["enemy_type"]
        self.enemy_count = enemy_count_dict["enemy_count"]
        self.num_enemy_kinds = len(self.enemy_type)

        self.initialize_phase()

    def initialize_phase(self):
        self.score_offset = player_score
        self.current_score = 0

        self.frames_to_clear = 0
        self.cleared = False

    def update(self):
        for e in range(self.num_enemy_kinds):
            if len(self.enemy_type[e].group) < self.enemy_count[e]:
                self.enemy_type[e]()

        self.current_score = player_score - self.score_offset
        self.frames_to_clear += 1
        self.elapsed_time = self.frames_to_clear / FPS

        if self.current_score >= self.required_score:
            self.cleared = True

    def is_cleared(self):
        return self.cleared


class BossPhase:
    def __init__(self, boss_class, enemy_count_dict):
        self.current_score = 0
        self.score_offset = 0

        self.frames_to_clear = 0
        self.elapsed_time = 0
        self.cleared = False

        self.enemy_type = enemy_count_dict["enemy_type"]
        self.enemy_count = enemy_count_dict["enemy_count"]
        self.num_enemy_kinds = len(self.enemy_type)

        self.boss_class = boss_class
        self.boss = None

    def initialize_phase(self):
        self.score_offset = player_score
        self.current_score = 0

        self.frames_to_clear = 0
        self.cleared = False

        self.boss = None

    def generate_boss(self):
        self.boss = self.boss_class()

    def update(self):
        for e in range(self.num_enemy_kinds):
            if len(self.enemy_type[e].group) < self.enemy_count[e]:
                self.enemy_type[e]()

        self.current_score = player_score - self.score_offset
        self.frames_to_clear += 1
        self.elapsed_time = self.frames_to_clear / FPS

        if not self.boss.alive():
            self.cleared = True

    def is_cleared(self):
        return self.cleared

"""
all_levels = []

level_1 = Level()
level_1.add_phase(NormalPhase(required_score=200,
                              enemy_count_dict={"enemy_type": [StraightLineMover1],
                                                "enemy_count": [120]}))
level_1.add_phase(NormalPhase(required_score=400,
                              enemy_count_dict={"enemy_type": [StraightLineMover1,
                                                               StraightLineMover2],
                                                "enemy_count": [160, 40]}))
level_1.add_phase(NormalPhase(required_score=800,
                              enemy_count_dict={"enemy_type": [StraightLineMover1,
                                                               StraightLineMover2,
                                                               StraightLineMover3],
                                                "enemy_count": [200, 70, 30]}))
all_levels.append(level_1)
"""