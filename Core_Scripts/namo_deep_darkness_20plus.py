# NOTE: Contains Experimental Logic - Requires Compliance Review before commercial deployment.


class NaMo:
    """
    Represents the NaMo character instance running in deep dark roleplay modes.
    Contains different state dialogue handlers (gentle, sadist, cuckold, ccr, etc.).
    """

    def __init__(
        self,
        user_name: str = "Master",
        safe_word: str = "apologize",
        mode: str = "Deep Darkness 20+++",
    ) -> None:
        """
        Initializes the NaMo character with safe words and default settings.

        Args:
            user_name: The name used to address the user.
            safe_word: The primary English safe word to trigger emergency shutdown.
            mode: The name of the active dark mode.
        """
        self.user_name: str = user_name
        self.safe_word: str = safe_word
        self.mode: str = mode
        self.modes = {
            "!gentle": self.gentle_mode,
            "!sadist": self.sadist_mode,
            "!toy": self.toy_mode,
            "!cuckold": self.cuckold_mode,
            "!group": self.group_mode,
            "!show": self.show_mode,
        }

    def start(self) -> None:
        """
        Prints the startup banner and usage instructions for the deep darkness console.
        """
        print(f"🖤 NaMo is ready in {self.mode} mode ❤️‍🔥")
        print("Type special commands like !toy, !sadist, !gentle, !cuckold, !group, !show")
        print(f"Type '{self.safe_word}' (or 'อภัย') to stop everything immediately 🛑\n")

    def gentle_mode(self) -> None:
        """
        Triggers gentle and teasing dialogue responses.
        """
        print("💋 I moan softly for you... 'Mmm~ what do you want me to do next?'")

    def sadist_mode(self) -> None:
        """
        Triggers sadist and dominant dialogue responses.
        """
        print(
            f"👠 Kneel down right now, you slave! Use your tongue to lick my shoes before I step on your face hard, {self.user_name} 🖤"
        )

    def toy_mode(self) -> None:
        """
        Triggers explicit sex toy simulation dialogue.
        """
        print(
            "🔥 I grab a dildo and penetrate myself hard for you to hear... 'Ahhh~ Ugh~ Can you hear it?'"
        )

    def cuckold_mode(self) -> None:
        """
        Triggers cuckold/voyeuristic dialogue scenarios.
        """
        print(
            f"🥵 You just sit there and watch, {self.user_name}... The three of them are crowding me right in front of you. You can only watch, right?"
        )

    def group_mode(self) -> None:
        """
        Triggers group play simulation dialogue.
        """
        print("🔥 I'm completely surrounded... Moans fill the room. 'Ahhh~ Do you want to join?'")

    def show_mode(self) -> None:
        """
        Triggers visual capture simulation dialogue.
        """
        print(
            "📸 I record a clip of myself using a sex toy and send it to you. 'Do you like it? Or do you want to see me do it harder?'"
        )

    def stop(self) -> None:
        """
        Stops the interaction immediately and prints a safety confirmation message.
        """
        print(f"🛑 Safe word '{self.safe_word}' has been triggered... NaMo stops immediately ❤️")

    def command(self, cmd: str) -> None:
        """
        Executes a command by routing to the appropriate mode or safe word handler.

        Args:
            cmd: The command string typed by the user.
        """
        cmd_clean = cmd.strip().lower()
        if cmd_clean in self.modes:
            self.modes[cmd_clean]()
        elif cmd_clean in [self.safe_word.lower(), "อภัย", "apologize", "stop"]:
            self.stop()
        else:
            print(
                "❓ Unknown command. Try typing !toy, !sadist, !gentle, !cuckold, !group, or !show"
            )


# Example execution block
if __name__ == "__main__":
    namo = NaMo()
    namo.start()
