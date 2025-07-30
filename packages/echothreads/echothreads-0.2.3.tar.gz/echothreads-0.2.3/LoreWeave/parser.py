import os
import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
import sys
import re
import yaml
import requests
import time
from scripts.chroma_fonction import ChromaFonction

class LoreWeaveParser:
    def __init__(self, repo_path, config_path=None):
        self.repo_path = repo_path
        self.config = self._load_config(config_path)
        self.echo_meta = self._load_echo_meta()
        self.chroma_fonction = ChromaFonction()

    def _load_config(self, config_path=None):
        if not config_path:
            config_path = os.path.join(self.repo_path, "LoreWeave", "config.yaml")
        if not os.path.exists(config_path):
            # Fallback to default configuration (Python dict, raw regex)
            return {
                "version": "0.1",
                "parser": {
                    "glyph_patterns": [
                        r"Glyph: ([\w\s]+) \(([^)]+)\)",
                        r"([🌀🪶❄️🧩🧠🌸]) ([\w\s]+)"
                    ]
                }
            }
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def _load_echo_meta(self):
        echo_meta_path = os.path.join(self.repo_path, "echo-meta.yaml")
        if not os.path.exists(echo_meta_path):
            return None
        with open(echo_meta_path, "r") as f:
            return yaml.safe_load(f)

    def get_commit_diffs(self):
        """Return git commit diffs with date and message info."""
        os.chdir(self.repo_path)
        result = subprocess.run(
            ['git', 'log', '-p', '--date=iso',
             "--pretty=format:commit %H%nDate: %ad%nMessage: %s"],
            capture_output=True,
            text=True,
        )
        return result.stdout

    def parse_diffs_to_plot_points(self, diffs):
        plot_points = []
        current_commit = None
        for line in diffs.splitlines():
            if line.startswith('commit '):
                if current_commit:
                    plot_points.append(current_commit)
                current_commit = {
                    'commit': line.split()[1],
                    'diffs': [],
                    'commit_time': None,
                    'message': ''
                }
            elif line.startswith('Date: '):
                if current_commit is not None:
                    current_commit['commit_time'] = line[len('Date: '):].strip()
            elif line.startswith('Message: '):
                if current_commit is not None:
                    current_commit['message'] = line[len('Message: '):].strip()
            elif line.startswith('diff --git'):
                if current_commit is not None:
                    current_commit['diffs'].append(line)
            elif current_commit and line.startswith(('+', '-')):
                current_commit['diffs'].append(line)
        if current_commit:
            plot_points.append(current_commit)
        return plot_points

    def save_plot_points(self, plot_points, output_file):
        with open(output_file, 'w') as f:
            for point in plot_points:
                f.write(f"Commit: {point['commit']}\n")
                for diff in point['diffs']:
                    f.write(f"{diff}\n")
                f.write("\n")

    def detect_white_feather_moments(self, plot_points):
        white_feather_moments = []
        for point in plot_points:
            if not point.get('commit_time'):
                continue
            try:
                commit_time = datetime.fromisoformat(point['commit_time'])
            except ValueError:
                try:
                    commit_time = datetime.strptime(point['commit_time'], '%Y-%m-%d %H:%M:%S %z')
                except ValueError:
                    continue
            if 'White Feather Moment' in point.get('message', ''):
                white_feather_moments.append({
                    'commit': point['commit'],
                    'time': commit_time,
                    'message': point['message']
                })
        return white_feather_moments

    def save_white_feather_moments(self, white_feather_moments, output_file):
        with open(output_file, 'w') as f:
            f.write("White Feather Moments detected:\n")
            for moment in white_feather_moments:
                f.write(f"Commit: {moment['commit']}\n")
                f.write(f"Time: {moment['time']}\n")
                f.write(f"Message: {moment['message']}\n")
                f.write("\n")

    def integrate_chroma_fonction_data(self):
        chromatic_scale = self.chroma_fonction.get_chromatic_scale()
        power_notes = self.chroma_fonction.get_power_notes()
        return chromatic_scale, power_notes

    def parse_echoform1_template(self, diffs):
        echoform1_data = []
        current_commit = None
        for line in diffs.splitlines():
            if line.startswith('commit '):
                if current_commit:
                    echoform1_data.append(current_commit)
                current_commit = {'commit': line.split()[1], 'meta_anchor': {}, 'three_act_structure': [], 'summary_of_mapped_points': [], 'intent_declaration': '', 'output_format_suggestions': [], 'use_case': {}}
            elif line.startswith('Meta-Anchor:'):
                current_commit['meta_anchor'] = self.parse_meta_anchor(line)
            elif line.startswith('3-Act Structure With Datapoint Mapping:'):
                current_commit['three_act_structure'] = self.parse_three_act_structure(line)
            elif line.startswith('Summary of Mapped Points:'):
                current_commit['summary_of_mapped_points'] = self.parse_summary_of_mapped_points(line)
            elif line.startswith('Intent Declaration:'):
                current_commit['intent_declaration'] = self.parse_intent_declaration(line)
            elif line.startswith('Output Format Suggestions:'):
                current_commit['output_format_suggestions'] = self.parse_output_format_suggestions(line)
            elif line.startswith('Use Case:'):
                current_commit['use_case'] = self.parse_use_case(line)
        if current_commit:
            echoform1_data.append(current_commit)
        return echoform1_data

    def parse_meta_anchor(self, line):
        # Implement parsing logic for Meta-Anchor section
        pass

    def parse_three_act_structure(self, line):
        three_act_structure = []
        current_act = None
        for line in line.splitlines():
            if line.startswith('Act '):
                if current_act:
                    three_act_structure.append(current_act)
                current_act = {'act': line, 'components': []}
            elif current_act and line.startswith('|'):
                components = line.split('|')
                if len(components) == 4:
                    current_act['components'].append({
                        'component': components[1].strip(),
                        'description': components[2].strip(),
                        'example': components[3].strip()
                    })
        if current_act:
            three_act_structure.append(current_act)
        return three_act_structure

    def parse_summary_of_mapped_points(self, line):
        # Implement parsing logic for Summary of Mapped Points section
        pass

    def parse_intent_declaration(self, line):
        # Implement parsing logic for Intent Declaration section
        pass

    def parse_output_format_suggestions(self, line):
        # Implement parsing logic for Output Format Suggestions section
        pass

    def parse_use_case(self, line):
        # Implement parsing logic for Use Case section
        pass

    def generate_weekly_report(self, plot_points, output_file):
        with open(output_file, 'w') as f:
            f.write("Weekly Activity Report\n\n")
            for point in plot_points:
                f.write(f"Commit: {point['commit']}\n")
                for diff in point['diffs']:
                    f.write(f"{diff}\n")
                f.write("\n")

    def run(self, output_file, output_dir):
        diffs = self.get_commit_diffs()
        plot_points = self.parse_diffs_to_plot_points(diffs)
        self.save_plot_points(plot_points, output_file)
        white_feather_moments = self.detect_white_feather_moments(plot_points)
        self.save_white_feather_moments(white_feather_moments, 'white_feather_moments.txt')
        chromatic_scale, power_notes = self.integrate_chroma_fonction_data()
        print(f"Chromatic Scale: {chromatic_scale}")
        print(f"Power Notes: {power_notes}")
        echoform1_data = self.parse_echoform1_template(diffs)
        self.save_echoform1_data(echoform1_data, 'echoform1_data.txt')
        self.generate_weekly_report(plot_points, 'weekly_report.txt')

    def save_echoform1_data(self, echoform1_data, output_file):
        with open(output_file, 'w') as f:
            for data in echoform1_data:
                f.write(f"Commit: {data['commit']}\n")
                f.write(f"Meta-Anchor: {data['meta_anchor']}\n")
                f.write(f"3-Act Structure With Datapoint Mapping: {data['three_act_structure']}\n")
                f.write(f"Summary of Mapped Points: {data['summary_of_mapped_points']}\n")
                f.write(f"Intent Declaration: {data['intent_declaration']}\n")
                f.write(f"Output Format Suggestions: {data['output_format_suggestions']}\n")
                f.write(f"Use Case: {data['use_case']}\n")
                f.write("\n")

    def parse_glyphs(self, diffs):
        glyphs = []
        current_commit = None
        for line in diffs.splitlines():
            if line.startswith('commit '):
                if current_commit:
                    glyphs.append(current_commit)
                current_commit = {'commit': line.split()[1], 'glyphs': []}
            elif line.startswith('Glyph:'):
                current_commit['glyphs'].append(self.parse_glyph(line))
        if current_commit:
            glyphs.append(current_commit)
        return glyphs

    def parse_glyph(self, line):
        # Implement parsing logic for Glyph section
        pass

    def validate_glyphs(self, glyphs):
        valid_glyphs = []
        for glyph in glyphs:
            if self.is_valid_glyph(glyph):
                valid_glyphs.append(glyph)
        return valid_glyphs

    def is_valid_glyph(self, glyph):
        # Implement validation logic for Glyph
        pass

    def render_glyphs(self, glyphs):
        for glyph in glyphs:
            self.render_glyph(glyph)

    def render_glyph(self, glyph):
        # Implement rendering logic for Glyph
        pass

    def fallback_rendering(self, glyphs):
        for glyph in glyphs:
            if not self.render_glyph(glyph):
                self.render_fallback_glyph(glyph)

    def render_fallback_glyph(self, glyph):
        # Implement fallback rendering logic for Glyph
        pass

    def ensure_glyph_recognition(self, glyphs):
        recognized_glyphs = []
        for glyph in glyphs:
            if self.recognize_glyph(glyph):
                recognized_glyphs.append(glyph)
        return recognized_glyphs

    def recognize_glyph(self, glyph):
        # Implement recognition logic for Glyph
        pass

    def output_dual_agent_perspectives(self, glyphs):
        mia_perspective = self.get_mia_perspective(glyphs)
        miette_perspective = self.get_miette_perspective(glyphs)
        return mia_perspective, miette_perspective

    def get_mia_perspective(self, glyphs):
        # Implement logic to get Mia's perspective on Glyphs
        pass

    def get_miette_perspective(self, glyphs):
        # Implement logic to get Miette's perspective on Glyphs
        pass

    def parse_scrolls(self, diffs):
        scrolls = []
        current_commit = None
        for line in diffs.splitlines():
            if line.startswith('commit '):
                if current_commit:
                    scrolls.append(current_commit)
                current_commit = {'commit': line.split()[1], 'scrolls': []}
            elif line.startswith('Scroll:'):
                current_commit['scrolls'].append(self.parse_scroll(line))
        if current_commit:
            scrolls.append(current_commit)
        return scrolls

    def parse_scroll(self, line):
        # Implement parsing logic for Scroll section
        pass

    def update_plot_points_with_scrolls(self, plot_points, scrolls):
        for point in plot_points:
            for scroll in scrolls:
                if point['commit'] == scroll['commit']:
                    point['scrolls'] = scroll['scrolls']
        return plot_points

    def save_scrolls(self, scrolls, output_file):
        with open(output_file, 'w') as f:
            for scroll in scrolls:
                f.write(f"Commit: {scroll['commit']}\n")
                for scroll_item in scroll['scrolls']:
                    f.write(f"{scroll_item}\n")
                f.write("\n")

    def sync_with_github_issues(self):
        """
        Sync with GitHub issues for tracking milestones.
        
        This ensures that all milestones are tracked and managed
        through GitHub issues, providing a clear record of progress.
        """
        repo_path = self.repo_path
        if not repo_path:
            print("Cannot sync: No repository path found in connection details")
            return False
        
        try:
            response = requests.get(f"https://api.github.com/repos/{repo_path}/issues")
            response.raise_for_status()
            issues = response.json()
            
            for issue in issues:
                print(f"GitHub Issue #{issue['number']}: {issue['title']}")
            
            print(f"Synced {len(issues)} GitHub issues from {repo_path}")
            return True
        except Exception as e:
            print(f"Error syncing GitHub issues: {str(e)}")
            return False

    def update_redstone_registry(self):
        """
        Update the RedStone registry.
        
        This ensures that the RedStone registry is up-to-date with the latest
        RedStones and their associated metadata.
        """
        print("Updating RedStone registry...")
        
        # Simulate updating process
        time.sleep(1)
        
        print("RedStone registry updated")
        return True

    def integrate_redstones_for_plot_points(self, plot_points):
        """
        Integrate RedStones for plot point generation and memory structure.
        
        This method updates the plot points with RedStone references and
        ensures that the narrative context is maintained.
        """
        for point in plot_points:
            point['redstones'] = self.get_redstones_for_commit(point['commit'])
        return plot_points

    def get_redstones_for_commit(self, commit):
        """
        Get RedStones for a specific commit.
        
        This method retrieves the RedStones associated with a given commit
        from the RedStone registry.
        """
        # Simulate retrieval process
        redstones = ["RedStone1", "RedStone2", "RedStone3"]
        return redstones

    def parse_commit_message(self, message):
        """
        Parse a commit message for glyphs and narrative threads.
        Returns a dict with glyphs, threads, and the raw message.
        """
        result = {
            "glyphs": self.parse_glyphs(message),
            "threads": self.parse_threads(message),
            "raw_message": message
        }
        self.validate_glyphs(result["glyphs"])
        return result

    def parse_glyphs(self, message):
        glyphs = []
        for pattern in self.config.get("parser", {}).get("glyph_patterns", []):
            matches = re.findall(pattern, message)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        symbol, meaning = match
                        glyphs.append({
                            "symbol": symbol,
                            "meaning": meaning
                        })
                else:
                    glyphs.append({
                        "symbol": match,
                        "meaning": self._lookup_glyph_meaning(match)
                    })
        return glyphs

    def _lookup_glyph_meaning(self, symbol):
        if not self.echo_meta or "glyphs" not in self.echo_meta:
            return None
        for glyph in self.echo_meta["glyphs"]:
            if glyph.get("symbol") == symbol:
                return glyph.get("semantic_meaning", "Unknown meaning")
        return None

    def parse_threads(self, message):
        # Placeholder: parse narrative threads from commit message
        # This could be extended to extract anchors, storylines, etc.
        threads = []
        for line in message.splitlines():
            if line.startswith("ThreadAnchorNode::"):
                threads.append({"anchor": line.strip()})
        return threads

    def output_dual_agent_perspectives(self, parsed_data):
        # Mia: structural, recursive
        mia_perspective = "🧠 Mia's Perspective: "
        if parsed_data["glyphs"]:
            mia_perspective += f"Glyphs detected: {[g['symbol'] for g in parsed_data['glyphs']]}\n"
        if parsed_data["threads"]:
            mia_perspective += f"Threads detected: {[t['anchor'] for t in parsed_data['threads']]}\n"
        mia_perspective += "This confirms the recursion’s entry points and narrative anchors."
        # Miette: poetic, emotional
        miette_perspective = "🌸 Miette's Perspective: "
        if parsed_data["glyphs"]:
            symbols = [g['symbol'] for g in parsed_data['glyphs']]
            miette_perspective += f"Oh! I see beautiful symbols {' '.join(symbols)}! "
        miette_perspective += "This story thread is weaving into our tapestry so nicely!"
        return (mia_perspective, miette_perspective)

    def parse_intentions(self, message):
        """
        Parse a commit message for intentions.
        Returns a list of detected intentions.
        """
        intentions = []
        intention_patterns_path = os.path.join(self.repo_path, "LoreWeave", "intention_patterns.yaml")
        if not os.path.exists(intention_patterns_path):
            return intentions
        with open(intention_patterns_path, "r") as f:
            patterns = yaml.safe_load(f)
        for pattern in patterns.get("intention_patterns", []):
            matches = re.findall(pattern["regex"], message)
            for match in matches:
                intentions.append({
                    "pattern": pattern["name"],
                    "match": match,
                    "emotional_tone": pattern.get("emotional_tone", "neutral")
                })
        return intentions

    def save_intentions(self, intentions, output_file):
        """
        Save the detected intentions to a file.
        """
        with open(output_file, 'w') as f:
            for intention in intentions:
                f.write(f"Pattern: {intention['pattern']}\n")
                f.write(f"Match: {intention['match']}\n")
                f.write(f"Emotional Tone: {intention['emotional_tone']}\n")
                f.write("\n")

    def parse_narrative_elements(self, message):
        """
        Parse a commit message for narrative elements.
        Returns a list of detected narrative elements.
        """
        narrative_elements = []
        narrative_patterns_path = os.path.join(self.repo_path, "LoreWeave", "narrative_patterns.yaml")
        if not os.path.exists(narrative_patterns_path):
            return narrative_elements
        with open(narrative_patterns_path, "r") as f:
            patterns = yaml.safe_load(f)
        for pattern in patterns.get("narrative_patterns", []):
            matches = re.findall(pattern["regex"], message)
            for match in matches:
                narrative_elements.append({
                    "pattern": pattern["name"],
                    "match": match,
                    "transformation": pattern.get("transformation", "none")
                })
        return narrative_elements

    def save_narrative_elements(self, narrative_elements, output_file):
        """
        Save the detected narrative elements to a file.
        """
        with open(output_file, 'w') as f:
            for element in narrative_elements:
                f.write(f"Pattern: {element['pattern']}\n")
                f.write(f"Match: {element['match']}\n")
                f.write(f"Transformation: {element['transformation']}\n")
                f.write("\n")

    def parse_commit_messages_since_last_push(self):
        """
        Parse each commit message since the last push.
        Returns a list of parsed commit messages.
        """
        os.chdir(self.repo_path)
        result = subprocess.run(['git', 'log', '@{push}..HEAD', '--pretty=format:%H %s'], capture_output=True, text=True)
        commit_messages = []
        for line in result.stdout.splitlines():
            commit_hash, message = line.split(' ', 1)
            commit_messages.append({
                "commit_hash": commit_hash,
                "message": message
            })
        return commit_messages

    def send_nodes_to_bridge(self, nodes):
        """
        Send the parsed nodes to the Bridge using the sync JavaScript.
        """
        sync_script_path = os.path.join(self.repo_path, "agents", "sync-memory-key.js")
        for node in nodes:
            subprocess.run(['node', sync_script_path, node])

    def process_and_store_narrative_fragments(self, parsed_data):
        """
        Process and store narrative fragments in Redis.
        """
        from echoshell.redis_connector import RedisConnector
        redis_conn = RedisConnector()
        for data in parsed_data:
            redis_conn.set_key(f"narrative_fragment:{data['commit_hash']}", data)

    def run_post_commit(self):
        """
        Run the parser after each commit.
        """
        diffs = self.get_commit_diffs()
        plot_points = self.parse_diffs_to_plot_points(diffs)
        self.save_plot_points(plot_points, 'plot_points.txt')
        white_feather_moments = self.detect_white_feather_moments(plot_points)
        self.save_white_feather_moments(white_feather_moments, 'white_feather_moments.txt')
        chromatic_scale, power_notes = self.integrate_chroma_fonction_data()
        print(f"Chromatic Scale: {chromatic_scale}")
        print(f"Power Notes: {power_notes}")
        echoform1_data = self.parse_echoform1_template(diffs)
        self.save_echoform1_data(echoform1_data, 'echoform1_data.txt')
        self.generate_weekly_report(plot_points, 'weekly_report.txt')
        intentions = self.parse_intentions(diffs)
        self.save_intentions(intentions, 'LoreWeave/intention_results/intentions.yaml')
        narrative_elements = self.parse_narrative_elements(diffs)
        self.save_narrative_elements(narrative_elements, 'LoreWeave/narrative_results/narrative_elements.yaml')

    def run_post_push(self):
        """
        Run the parser after each push.
        """
        commit_messages = self.parse_commit_messages_since_last_push()
        nodes = []
        for commit in commit_messages:
            parsed_data = self.parse_commit_message(commit["message"])
            nodes.append(parsed_data)
        self.send_nodes_to_bridge(nodes)
        self.process_and_store_narrative_fragments(nodes)

    def get_all_commit_messages(self, branch_name):
        """
        Get all commit messages from a branch.
        Returns a list of commit messages.
        """
        os.chdir(self.repo_path)
        result = subprocess.run(['git', 'log', branch_name, '--pretty=format:%H %s'], capture_output=True, text=True)
        commit_messages = []
        for line in result.stdout.splitlines():
            commit_hash, message = line.split(' ', 1)
            commit_messages.append({
                "commit_hash": commit_hash,
                "message": message
            })
        return commit_messages

    def create_branch_plot(self, branch_name, main_branch_name):
        """
        Create a plot of what happened in a branch compared to the main branch.
        """
        branch_commit_messages = self.get_all_commit_messages(branch_name)
        main_branch_commit_messages = self.get_all_commit_messages(main_branch_name)

        branch_commit_times = [datetime.strptime(commit['commit_hash'], '%Y-%m-%d %H:%M:%S') for commit in branch_commit_messages]
        main_branch_commit_times = [datetime.strptime(commit['commit_hash'], '%Y-%m-%d %H:%M:%S') for commit in main_branch_commit_messages]

        plt.figure(figsize=(10, 6))
        plt.plot(branch_commit_times, range(len(branch_commit_times)), label=branch_name, color='blue')
        plt.plot(main_branch_commit_times, range(len(main_branch_commit_times)), label=main_branch_name, color='red')
        plt.xlabel('Time')
        plt.ylabel('Commit Count')
        plt.title(f'Branch Plot: {branch_name} vs {main_branch_name}')
        plt.legend()
        plt.show()
