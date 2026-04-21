class Songs:
    """
    The song's lyrics and filepath are stored

    Attributes:
        lyrics, a string representing the lyrics of the song. With each line seperated with a newline escape key
        filepath, a string representing the filepath of the song
        song_name, a string representing the name of a song
    """

    def __init__(self, name):
        self.song_name = name
        self.lyrics = ""
        self.filepath = ""

    def set_lyrics(self):
        self.lyrics = """We're no strangers to love
        You know the rules and so do I
        A full commitment's what I'm thinking of
        You wouldn't get this from any other guy
        I just wanna tell you how I'm feeling
        Gotta make you understand
        Never gonna give you up
        Never gonna let you down
        Never gonna run around and desert you
        Never gonna make you cry
        Never gonna say goodbye
        Never gonna tell a lie and hurt you
        We've known each other for so long
        Your heart's been aching, but you're too shy to say it
        Inside, we both know what's been going on
        We know the game, and we're gonna play it
        And if you ask me how I'm feeling
        Don't tell me you're too blind to see
        Never gonna give you up
        Never gonna let you down
        Never gonna run around and desert you
        Never gonna make you cry
        Never gonna say goodbye
        Never gonna tell a lie and hurt you
        Never gonna give you up
        Never gonna let you down
        Never gonna run around and desert you
        Never gonna make you cry
        Never gonna say goodbye
        Never gonna tell a lie and hurt you
        Ooh (Give you up)
        Ooh-ooh (Give you up)
        Ooh (Never gonna give, never gonna give)
        Give you up
        Ooh-ooh (Never gonna give, never gonna give)
        Give you up
        We've known each other for so long
        Your heart's been aching, but you're too shy to say it
        Inside, we both know what's been going on
        We know the game, and we're gonna play it
        I just wanna tell you how I'm feeling
        Gotta make you understand
        Never gonna give you up
        Never gonna let you down
        Never gonna run around and desert you
        Never gonna make you cry
        Never gonna say goodbye
        Never gonna tell a lie and hurt you
        Never gonna give you up
        Never gonna let you down
        Never gonna run around and desert you
        Never gonna make you cry
        Never gonna say goodbye
        Never gonna tell a lie and hurt you
        Never gonna give you up
        Never gonna let you down
        Never gonna run around and desert you
        Never gonna make you cry
        Never gonna say goodbye
        Never gonna tell a lie and hurt you
        Never gonna give you up
        Never gonna let you down
        Never gonna run around and desert you
        Never gonna make you cry
        Never gonna say goodbye
        Never gonna tell a lie and hurt you"""

    def return_lyrics(self):
        self.set_lyrics()
        return self.lyrics


Test_song = Songs("Never Going to Give You Up")
print(Test_song.return_lyrics())
