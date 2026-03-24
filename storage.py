import json
import os
from datetime import datetime


class Storage:
    """Saves and loads game scores using JSON file.

    Features: CRUD, search, sort, filter, summary report.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.records = []
        self.load()

    # SAVE & LOAD

    def load(self):
        """Load scores from JSON file."""
        if not os.path.exists(self.filepath):
            self.records = []
            return
        try:
            with open(self.filepath, "r") as file:
                self.records = json.load(file)
        except json.JSONDecodeError:
            print("Warning: corrupted file. Starting fresh.")
            self.records = []

    def save(self):
        """Save all scores to JSON file."""
        with open(self.filepath, "w") as file:
            json.dump(self.records, file, indent=2)

    # CREATE

    def add_score(self, player_name, score, level):
        """Add a new score record."""
        # validate name
        if not player_name or not player_name.strip():
            player_name = "Anonymous"
        player_name = player_name.strip()[:15]

        # validate score
        if not isinstance(score, int) or score < 0:
            score = 0

        # create new id
        if self.records:
            new_id = max(r["id"] for r in self.records) + 1
        else:
            new_id = 1

        record = {
            "id": new_id,
            "player_name": player_name,
            "score": score,
            "level": level,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.records.append(record)
        self.save()
        return record

    # READ 

    def get_all(self):
        """Get all score records."""
        return self.records

    def get_by_id(self, record_id):
        """Get one record by its ID."""
        for record in self.records:
            if record["id"] == record_id:
                return record
        return None

    # UPDATE 

    def update_name(self, record_id, new_name):
        """Update player name for a record."""
        record = self.get_by_id(record_id)
        if record is None:
            print(f"Record {record_id} not found.")
            return False
        if not new_name or not new_name.strip():
            print("Name cannot be empty.")
            return False
        record["player_name"] = new_name.strip()[:15]
        self.save()
        return True

    # DELETE 

    def delete_score(self, record_id):
        """Delete a score record by ID."""
        record = self.get_by_id(record_id)
        if record is None:
            print(f"Record {record_id} not found.")
            return False
        self.records.remove(record)
        self.save()
        return True

    # SEARCH

    def search_by_name(self, name):
        """Search scores by player name (partial match)."""
        if not name or not name.strip():
            return []
        name = name.strip().lower()
        results = []
        for record in self.records:
            if name in record["player_name"].lower():
                results.append(record)
        return results

    #  SORT

    def get_top_scores(self, limit=10):
        """Get top scores sorted highest to lowest."""
        sorted_records = sorted(self.records,
                                   key=lambda r: r["score"],
                                   reverse=True)
        return sorted_records[:limit]

    def sort_by_date(self):
        """Get scores sorted by date (newest first)."""
        return sorted(self.records,
                       key=lambda r: r["date"],
                       reverse=True)

    def sort_by_level(self):
        """Get scores sorted by level (highest first)."""
        return sorted(self.records,
                       key=lambda r: r["level"],
                       reverse=True)

    # FILTER

    def filter_by_min_score(self, min_score):
        """Get records with score >= min_score."""
        return [r for r in self.records
                if r["score"] >= min_score]

    def filter_by_level(self, level):
        """Get records that reached a specific level."""
        return [r for r in self.records
                if r["level"] >= level]

    # SUMMARY 

    def get_summary(self):
        """Generate summary report of all games."""
        if not self.records:
            return None
        all_scores = [r["score"] for r in self.records]
        total = len(self.records)
        average = round(sum(all_scores) / total, 1)
        highest = max(all_scores)
        lowest = min(all_scores)
        best_level = max(r["level"] for r in self.records)

        return {
            "total_games": total,
            "average_score": average,
            "highest_score": highest,
            "lowest_score": lowest,
            "best_level": best_level
        }