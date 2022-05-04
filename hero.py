class Hero:
    bot = None
    @classmethod
    def set_bot(cls, bot):
        cls.bot = bot

    def __init__(self, group_name, transporter):
        self.group_name = group_name
        self.verified = False
        self.transporter = transporter
        self.health = 200
        self.strength_multiplier = 1
        self.items = []
        self.base_level = 1
        self.hero_level = 1  # Should be None
        self.using_potion = False
        
    def message(self, text):
        Hero.bot.send_message(
            chat_id=self.transporter,
            text=text)
        
        
class CaptainAmerica(Hero):
    def __init__(self, group_name, transporter):
        super().__init__(group_name, transporter)
        self.health = 300
        
        
class Hulk(Hero):
    def __init__(self, group_name, transporter):
        super().__init__(group_name, transporter)
        self.strength_multiplier = 1.5
    

HEROS = {
    'bat_girl': CaptainAmerica,
    'captain_america': CaptainAmerica,
    'jesse_quick': CaptainAmerica,
    'iron_man': CaptainAmerica,
    'groot': CaptainAmerica,
    'six_sense': CaptainAmerica,
    'hulk': Hulk
}
