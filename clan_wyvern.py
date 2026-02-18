import os
import json
from dotenv import load_dotenv
from grimoorum.memory_manager import Grimoorum
from eyrie.phoenix_gate import PhoenixGate

# Initialize Environment
load_dotenv()


class CastleWyvern:
    def __init__(self):
        self.clan_name = "Manhattan Clan"
        self.status = self._load_heartbeat()

        # Load the Council's Spells (Full Manhattan Clan)
        self.spells = {
            # Core Clan (Original Four)
            "goliath": self._load_spell("goliath_system.md"),
            "lexington": self._load_spell("lexington_system.md"),
            "brooklyn": self._load_spell("brooklyn_system.md"),
            "broadway": self._load_spell("broadway_system.md"),
            # Extended Clan (New Members)
            "hudson": self._load_spell("hudson_system.md"),
            "bronx": self._load_spell("bronx_system.md"),
            "elisa": self._load_spell("elisa_system.md"),
            "xanatos": self._load_spell("xanatos_system.md"),
            "demona": self._load_spell("demona_system.md"),
        }

        self.vault = Grimoorum()
        self.gate = PhoenixGate()

    def _load_heartbeat(self):
        """Checks the status of the clan's nodes."""
        try:
            with open("eyrie/heartbeat.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"Status": "Unknown"}

    def _load_spell(self, filename):
        """Retrieves a system prompt from the /prompts directory."""
        path = os.path.join("prompts", filename)
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return f"The spell for {filename} remains unwritten."

    def summon_council(self, user_input):
        """Orchestrator logic: Goliath decides who should handle the task."""
        context = self.vault.consult_archives(limit=2)
        mode = "local" if self.status.get("Stone_Sentinel") == "AWAKE 🟢" else "cloud"

        print(f"\n[GOLIATH]: 'The clan is {mode}. I am convening the council.'")

        # Decision Engine - Routes to appropriate clan member
        query = user_input.lower()

        # Technical Tasks
        if any(
            word in query for word in ["code", "script", "fix", "terminal", "bug", "error", "debug"]
        ):
            agent, spell = "LEXINGTON", self.spells["lexington"]

        # Strategic Planning
        elif any(
            word in query for word in ["plan", "strategy", "choose", "versus", "options", "tactics"]
        ):
            agent, spell = "BROOKLYN", self.spells["brooklyn"]

        # Summarization & Research
        elif any(
            word in query
            for word in ["summarize", "read", "explain", "info", "document", "analyze"]
        ):
            agent, spell = "BROADWAY", self.spells["broadway"]

        # Archival & Historical Context
        elif any(
            word in query
            for word in ["history", "archive", "past", "remember", "before", "previous", "lesson"]
        ):
            agent, spell = "HUDSON", self.spells["hudson"]

        # Security & Monitoring
        elif any(
            word in query
            for word in [
                "security",
                "monitor",
                "alert",
                "threat",
                "scan",
                "check",
                "safe",
                "protect",
            ]
        ):
            agent, spell = "BRONX", self.spells["bronx"]

        # Human Context & Ethics
        elif any(
            word in query
            for word in ["human", "legal", "law", "people", "social", "public", "ethics", "fair"]
        ):
            agent, spell = "ELISA", self.spells["elisa"]

        # Red Team / Adversarial Testing
        elif any(
            word in query
            for word in [
                "test",
                "vulnerability",
                "exploit",
                "attack",
                "break",
                "hack",
                "weakness",
                "red team",
            ]
        ):
            agent, spell = "XANATOS", self.spells["xanatos"]

        # Failsafe / Worst-case
        elif any(
            word in query
            for word in [
                "fail",
                "worst",
                "disaster",
                "backup",
                "contingency",
                "what if",
                "could go wrong",
            ]
        ):
            agent, spell = "DEMONA", self.spells["demona"]

        # Default to Goliath
        else:
            agent, spell = "GOLIATH", self.spells["goliath"]

        # Cast the spell through the Phoenix Gate
        print(f"--- Calling upon {agent} ---")
        response = self.gate.call_ai(user_input, spell, mode=mode)
        print(f"[{agent}]: '{response}'")

        # Record to memory
        self.vault.record_interaction(user_input, f"Agent: {agent} | Response: {response}")


def main():
    wyvern = CastleWyvern()
    print("--- PROJECT CASTLE WYVERN: THE COUNCIL AWAKENS ---")

    while True:
        user_query = input("\nCommand the Council: ")
        if user_query.lower() == "sleep":
            print("\n[GOLIATH]: 'The sun rises. We return to stone.'")
            break

        wyvern.summon_council(user_query)


if __name__ == "__main__":
    main()
