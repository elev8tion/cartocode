#!/usr/bin/env python3
"""
UI Enhancement System for Cartographer
Provides reusable UI enhancement patterns for chat-driven optimization
"""

from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass
import json


class UIComponent(Enum):
    """Available UI components for enhancement"""
    CODE_EDITOR = "code_editor"
    FILE_TREE = "file_tree"
    TERMINAL = "terminal"
    CHAT_INTERFACE = "chat_interface"
    RISK_VISUALIZER = "risk_visualizer"
    GRAPH_VIEW = "graph_view"
    LIST_VIEW = "list_view"
    MATRIX_VIEW = "matrix_view"
    CONCERNS_VIEW = "concerns_view"


@dataclass
class UIEnhancement:
    """Represents a single UI enhancement"""
    component: UIComponent
    enhancement_type: str
    implementation: str
    priority: int = 1
    description: str = ""

    def apply(self, context: Dict) -> Dict:
        """Apply this enhancement to the given context"""
        return {
            "component": self.component.value,
            "enhancement": self.enhancement_type,
            "code_snippet": self.implementation,
            "context_applied": context,
            "priority": self.priority,
            "description": self.description
        }

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "component": self.component.value,
            "type": self.enhancement_type,
            "priority": self.priority,
            "description": self.description,
            "implementation": self.implementation
        }


class UIEnhancementRegistry:
    """Registry of reusable UI enhancements"""

    def __init__(self):
        self.enhancements: List[UIEnhancement] = []
        self._load_default_enhancements()

    def _load_default_enhancements(self):
        """Load all default UI enhancements"""

        # ═══════════════════════════════════════════════
        # CHAT INTERFACE ENHANCEMENTS
        # ═══════════════════════════════════════════════

        self.enhancements.extend([
            UIEnhancement(
                component=UIComponent.CHAT_INTERFACE,
                enhancement_type="code_suggestion_autocomplete",
                description="Auto-suggest code changes based on chat input",
                implementation="""
function enableCodeSuggestions(chatInput) {
    const suggestionBox = document.createElement('div');
    suggestionBox.className = 'suggestion-dropdown';
    chatInput.parentElement.appendChild(suggestionBox);

    chatInput.addEventListener('input', async (e) => {
        const text = e.target.value;
        if (text.includes('modify') || text.includes('add') || text.includes('fix')) {
            const suggestions = await fetchCodeSuggestions(text);
            displaySuggestions(suggestionBox, suggestions);
        } else {
            suggestionBox.style.display = 'none';
        }
    });
}

function displaySuggestions(box, suggestions) {
    box.innerHTML = suggestions.map(s => `
        <div class="suggestion-item" onclick="applySuggestion('${s.text}')">
            <span class="suggestion-icon">${s.icon}</span>
            <span class="suggestion-text">${s.text}</span>
        </div>
    `).join('');
    box.style.display = 'block';
}
                """,
                priority=1
            ),

            UIEnhancement(
                component=UIComponent.CHAT_INTERFACE,
                enhancement_type="message_reactions",
                description="Add emoji reactions to chat messages",
                implementation="""
function enableMessageReactions(messageElement) {
    const reactionsBar = document.createElement('div');
    reactionsBar.className = 'message-reactions';
    reactionsBar.innerHTML = `
        <button class="reaction-btn" data-emoji="👍" title="Helpful">👍</button>
        <button class="reaction-btn" data-emoji="❤️" title="Love it">❤️</button>
        <button class="reaction-btn" data-emoji="🤔" title="Confused">🤔</button>
        <button class="reaction-btn" data-emoji="⭐" title="Bookmark">⭐</button>
    `;

    messageElement.appendChild(reactionsBar);

    reactionsBar.querySelectorAll('.reaction-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('reacted');
            saveReaction(messageElement.id, btn.dataset.emoji);
        });
    });
}
                """,
                priority=2
            ),

            UIEnhancement(
                component=UIComponent.CHAT_INTERFACE,
                enhancement_type="voice_input",
                description="Add voice input capability to chat",
                implementation="""
function enableVoiceInput(chatInput) {
    const voiceBtn = document.createElement('button');
    voiceBtn.className = 'voice-input-btn';
    voiceBtn.innerHTML = '🎤';
    voiceBtn.title = 'Voice input';

    chatInput.parentElement.appendChild(voiceBtn);

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = false;
    recognition.interimResults = true;

    voiceBtn.addEventListener('click', () => {
        if (voiceBtn.classList.contains('recording')) {
            recognition.stop();
            voiceBtn.classList.remove('recording');
        } else {
            recognition.start();
            voiceBtn.classList.add('recording');
        }
    });

    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join('');
        chatInput.value = transcript;
    };

    recognition.onend = () => {
        voiceBtn.classList.remove('recording');
    };
}
                """,
                priority=3
            ),
        ])

        # ═══════════════════════════════════════════════
        # RISK VISUALIZER ENHANCEMENTS
        # ═══════════════════════════════════════════════

        self.enhancements.extend([
            UIEnhancement(
                component=UIComponent.RISK_VISUALIZER,
                enhancement_type="risk_heatmap",
                description="Add interactive risk heatmap overlay",
                implementation="""
function addRiskHeatmap(fileNodes, riskData) {
    fileNodes.forEach(node => {
        const risk = riskData[node.getAttribute('data-path')] || 0;
        const color = getRiskColor(risk);

        node.style.background = `linear-gradient(90deg, ${color}20 0%, transparent 100%)`;
        node.style.borderLeft = `3px solid ${color}`;
        node.setAttribute('data-risk', risk);

        // Add tooltip
        const tooltip = document.createElement('div');
        tooltip.className = 'risk-tooltip';
        tooltip.innerHTML = `Risk Score: ${risk}/100`;
        node.appendChild(tooltip);
    });
}

function getRiskColor(risk) {
    if (risk >= 75) return '#ef4444';  // red
    if (risk >= 50) return '#f97316';  // orange
    if (risk >= 25) return '#fbbf24';  // yellow
    return '#10b981';  // green
}
                """,
                priority=1
            ),

            UIEnhancement(
                component=UIComponent.RISK_VISUALIZER,
                enhancement_type="risk_timeline",
                description="Show risk changes over time",
                implementation="""
function createRiskTimeline(filePath, historicalData) {
    const timeline = document.createElement('div');
    timeline.className = 'risk-timeline';

    const canvas = document.createElement('canvas');
    canvas.width = 400;
    canvas.height = 100;
    timeline.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    const points = historicalData.map((d, i) => ({
        x: (i / historicalData.length) * canvas.width,
        y: canvas.height - (d.risk / 100 * canvas.height),
        risk: d.risk,
        date: d.date
    }));

    // Draw line
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();
    points.forEach((p, i) => {
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
    });
    ctx.stroke();

    // Draw points
    points.forEach(p => {
        ctx.fillStyle = getRiskColor(p.risk);
        ctx.beginPath();
        ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
        ctx.fill();
    });

    return timeline;
}
                """,
                priority=2
            ),
        ])

        # ═══════════════════════════════════════════════
        # GRAPH VIEW ENHANCEMENTS
        # ═══════════════════════════════════════════════

        self.enhancements.extend([
            UIEnhancement(
                component=UIComponent.GRAPH_VIEW,
                enhancement_type="dependency_path_highlighting",
                description="Highlight full dependency chains",
                implementation="""
function highlightDependencyChain(nodeId, graphData, direction = 'both') {
    const visited = new Set();
    const edges = new Set();

    function traverse(currentId, isForward) {
        if (visited.has(currentId)) return;
        visited.add(currentId);

        graphData.edges.forEach(edge => {
            const isRelevant = isForward
                ? edge.source === currentId
                : edge.target === currentId;

            if (isRelevant) {
                edges.add(edge.id);
                const nextId = isForward ? edge.target : edge.source;
                traverse(nextId, isForward);
            }
        });
    }

    if (direction === 'both' || direction === 'forward') {
        traverse(nodeId, true);
    }
    if (direction === 'both' || direction === 'backward') {
        traverse(nodeId, false);
    }

    // Apply highlighting
    visited.forEach(id => {
        const node = document.querySelector(`[data-node-id="${id}"]`);
        if (node) node.classList.add('dependency-highlight');
    });

    edges.forEach(id => {
        const edge = document.querySelector(`[data-edge-id="${id}"]`);
        if (edge) edge.classList.add('dependency-edge-highlight');
    });
}
                """,
                priority=1
            ),

            UIEnhancement(
                component=UIComponent.GRAPH_VIEW,
                enhancement_type="circular_dependency_detector",
                description="Visually highlight circular dependencies",
                implementation="""
function detectAndHighlightCircularDeps(graphData) {
    const cycles = [];
    const visited = new Set();
    const recStack = new Set();

    function dfs(nodeId, path = []) {
        if (recStack.has(nodeId)) {
            const cycleStart = path.indexOf(nodeId);
            cycles.push(path.slice(cycleStart).concat(nodeId));
            return;
        }

        if (visited.has(nodeId)) return;

        visited.add(nodeId);
        recStack.add(nodeId);
        path.push(nodeId);

        const outEdges = graphData.edges.filter(e => e.source === nodeId);
        outEdges.forEach(edge => dfs(edge.target, [...path]));

        recStack.delete(nodeId);
    }

    graphData.nodes.forEach(node => {
        if (!visited.has(node.id)) dfs(node.id);
    });

    // Highlight cycles
    cycles.forEach((cycle, i) => {
        cycle.forEach(nodeId => {
            const node = document.querySelector(`[data-node-id="${nodeId}"]`);
            if (node) {
                node.classList.add('circular-dependency');
                node.setAttribute('data-cycle', i);
            }
        });
    });

    return cycles;
}
                """,
                priority=1
            ),
        ])

        # ═══════════════════════════════════════════════
        # CODE EDITOR ENHANCEMENTS
        # ═══════════════════════════════════════════════

        self.enhancements.extend([
            UIEnhancement(
                component=UIComponent.CODE_EDITOR,
                enhancement_type="inline_risk_gutters",
                description="Show risk indicators in code editor gutter",
                implementation="""
function addInlineRiskIndicators(editor, riskAnalysis) {
    riskAnalysis.bindings.forEach(binding => {
        const line = binding.line;
        const riskLevel = binding.risk;

        // Add gutter marker
        const marker = editor.session.addGutterDecoration(
            line,
            `risk-gutter-${getRiskClass(riskLevel)}`
        );

        // Add line widget with details
        const widget = {
            row: line,
            fixedWidth: true,
            coverGutter: false,
            el: createRiskWidget(riskLevel, binding)
        };

        editor.session.addLineWidget(widget);
    });
}

function createRiskWidget(risk, binding) {
    const div = document.createElement('div');
    div.className = 'inline-risk-widget';
    div.innerHTML = `
        <span class="risk-icon" style="color: ${getRiskColor(risk)}">⚠️</span>
        <span class="risk-level">${risk}/100</span>
        <span class="risk-type">${binding.type}</span>
        <span class="risk-desc">${binding.description}</span>
    `;
    return div;
}

function getRiskClass(risk) {
    if (risk >= 75) return 'critical';
    if (risk >= 50) return 'high';
    if (risk >= 25) return 'medium';
    return 'low';
}
                """,
                priority=2
            ),

            UIEnhancement(
                component=UIComponent.CODE_EDITOR,
                enhancement_type="ai_code_lens",
                description="Show AI-powered code suggestions inline",
                implementation="""
function addAICodeLens(editor, analysis) {
    analysis.suggestions.forEach(suggestion => {
        const codeLens = {
            range: new Range(suggestion.line, 0, suggestion.line, 0),
            command: {
                title: `💡 ${suggestion.title}`,
                handler: () => applySuggestion(suggestion)
            }
        };

        editor.session.addCodeLens(codeLens);
    });
}

function applySuggestion(suggestion) {
    // Show diff preview
    showDiffPreview(suggestion.before, suggestion.after);

    // Apply on confirm
    if (confirm(`Apply: ${suggestion.description}?`)) {
        editor.session.replace(
            new Range(suggestion.startLine, 0, suggestion.endLine, 0),
            suggestion.after
        );
    }
}
                """,
                priority=3
            ),
        ])

        # ═══════════════════════════════════════════════
        # FILE TREE ENHANCEMENTS
        # ═══════════════════════════════════════════════

        self.enhancements.extend([
            UIEnhancement(
                component=UIComponent.FILE_TREE,
                enhancement_type="fuzzy_search_filter",
                description="Fuzzy search with scoring and highlighting",
                implementation="""
function enableFuzzyFileSearch(fileTree, searchInput) {
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const files = Array.from(fileTree.querySelectorAll('.file-item'));

        if (!query) {
            files.forEach(f => {
                f.style.display = '';
                f.style.opacity = '1';
            });
            return;
        }

        const scored = files.map(file => {
            const path = file.getAttribute('data-path').toLowerCase();
            const score = fuzzyMatchScore(query, path);
            return {file, score, path};
        });

        scored.sort((a, b) => b.score - a.score);

        scored.forEach(({file, score, path}) => {
            if (score > 0) {
                file.style.display = '';
                file.style.opacity = Math.min(1, score / 100);

                // Highlight matched characters
                file.innerHTML = highlightMatches(path, query);
            } else {
                file.style.display = 'none';
            }
        });
    });
}

function fuzzyMatchScore(query, text) {
    let score = 0;
    let queryIndex = 0;
    let previousMatchIndex = -1;

    for (let i = 0; i < text.length && queryIndex < query.length; i++) {
        if (text[i] === query[queryIndex]) {
            // Consecutive matches get bonus points
            if (previousMatchIndex === i - 1) {
                score += 10;
            } else {
                score += 5;
            }
            previousMatchIndex = i;
            queryIndex++;
        }
    }

    return queryIndex === query.length ? score : 0;
}

function highlightMatches(text, query) {
    let result = '';
    let queryIndex = 0;

    for (let i = 0; i < text.length; i++) {
        if (queryIndex < query.length && text[i] === query[queryIndex]) {
            result += `<mark>${text[i]}</mark>`;
            queryIndex++;
        } else {
            result += text[i];
        }
    }

    return result;
}
                """,
                priority=1
            ),

            UIEnhancement(
                component=UIComponent.FILE_TREE,
                enhancement_type="file_size_indicators",
                description="Visual indicators for file sizes",
                implementation="""
function addFileSizeIndicators(fileTree, sizeData) {
    fileTree.querySelectorAll('.file-item').forEach(item => {
        const path = item.getAttribute('data-path');
        const size = sizeData[path] || 0;

        const indicator = document.createElement('span');
        indicator.className = 'file-size-indicator';
        indicator.style.width = `${Math.min(size / 1000, 100)}px`;
        indicator.style.background = getSizeColor(size);
        indicator.title = formatFileSize(size);

        item.appendChild(indicator);
    });
}

function getSizeColor(bytes) {
    if (bytes > 100000) return '#ef4444';  // > 100KB
    if (bytes > 50000) return '#f97316';   // > 50KB
    if (bytes > 10000) return '#fbbf24';   // > 10KB
    return '#10b981';  // small files
}

function formatFileSize(bytes) {
    if (bytes >= 1000000) return `${(bytes / 1000000).toFixed(1)} MB`;
    if (bytes >= 1000) return `${(bytes / 1000).toFixed(1)} KB`;
    return `${bytes} B`;
}
                """,
                priority=2
            ),
        ])

    def get_enhancements_for_component(self, component: UIComponent) -> List[UIEnhancement]:
        """Get all enhancements for a specific component"""
        return [e for e in self.enhancements if e.component == component]

    def get_enhancement_by_type(self, enhancement_type: str) -> UIEnhancement:
        """Get enhancement by type"""
        for e in self.enhancements:
            if e.enhancement_type == enhancement_type:
                return e
        return None

    def add_enhancement(self, enhancement: UIEnhancement):
        """Add a custom enhancement to the registry"""
        self.enhancements.append(enhancement)

    def remove_enhancement(self, enhancement_type: str) -> bool:
        """Remove enhancement by type"""
        original_len = len(self.enhancements)
        self.enhancements = [e for e in self.enhancements if e.enhancement_type != enhancement_type]
        return len(self.enhancements) < original_len

    def apply_all_for_component(self, component: UIComponent, context: Dict = None) -> List[Dict]:
        """Apply all enhancements for a component"""
        enhancements = self.get_enhancements_for_component(component)
        enhancements.sort(key=lambda x: x.priority)
        return [e.apply(context or {}) for e in enhancements]

    def export_to_json(self, filepath: str):
        """Export all enhancements to JSON file"""
        data = {
            "version": "1.0",
            "enhancements": [e.to_dict() for e in self.enhancements]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def list_all(self) -> str:
        """List all enhancements in human-readable format"""
        output = ["UI Enhancement Registry:", "=" * 50]

        by_component = {}
        for e in self.enhancements:
            comp = e.component.value
            if comp not in by_component:
                by_component[comp] = []
            by_component[comp].append(e)

        for component, enhancements in sorted(by_component.items()):
            output.append(f"\n{component.upper()}")
            output.append("-" * 30)
            for e in sorted(enhancements, key=lambda x: x.priority):
                output.append(f"  [{e.priority}] {e.enhancement_type}")
                if e.description:
                    output.append(f"      → {e.description}")

        return "\n".join(output)


# Create global registry instance
registry = UIEnhancementRegistry()


if __name__ == "__main__":
    # Demo usage
    print(registry.list_all())
    print("\n" + "=" * 50)
    print(f"\nTotal enhancements: {len(registry.enhancements)}")

    # Export to JSON
    registry.export_to_json("ui_enhancements_export.json")
    print("\nExported to ui_enhancements_export.json")
