# VERA - Competition Submission - Capstone Project for Google ADK Course.

## The Problem: Disinformation in the Digital Age

We live in an era where false information spreads faster than truth. A single misleading social media post, articles can reach millions within hours, influencing people, undermining public health initiatives, and eroding trust in institutions. The COVID-19 pandemic demonstrated this danger vividly: health misinformation cost lives.

Traditional fact-checking faces insurmountable challenges. Professional fact-checkers spend 4-6 hours verifying a single article, checking only limited sources, and applying subjective criteria. This approach cannot scale to match the volume of content generated daily. Expert fact-checking costs $50-100 per hour, making it inaccessible to most individuals and small organizations. By the time professional fact-checkers debunk a claim, it has already gone viral.

## The Solution: VERA - AI-Powered Multi-Agent Fact-Checking

VERA (Virtual Evidence & Reality Assessment) is an AI-powered system that democratizes fact-checking by analyzing text for disinformation and manipulation in 2-3 minutes. Unlike traditional single-LLM approaches, VERA employs six specialized Gemini 2.5 Flash agents working in sequence, each mastering a specific aspect of analysis.

### The Six Agents:

**Researcher Agent** - The fact-checker. Uses Google Search (Grounding API) to verify factual claims against reliable sources. Identifies 3-5 key claims and determines if each is True, False, or Unverified, citing independent sources.

**Librarian Agent** - The context provider. Searches Wikipedia for encyclopedic background information, definitions, and historical context. Complements the Researcher's real-time news with stable, authoritative knowledge.

**Analyst Agent** - The manipulation detector. Identifies propaganda techniques (bandwagon, fear-mongering), emotional appeals, loaded language, and logical fallacies (straw man, false dilemma, ad hominem). Uses pure LLM reasoning without external tools.

**Critic Agent** - The quality controller. Acts as an independent reviewer, challenging the Researcher's fact-checking and the Analyst's manipulation findings. Identifies potential biases, gaps, and alternative explanations. This cross-validation layer significantly reduces AI hallucinations.

**Scoring Agent** - The quantitative assessor. Synthesizes all findings into three objective metrics on a 1-10 scale: Potential Disinformation Level (1=truthful, 10=completely false), Potential Manipulation Level (1=neutral, 10=highly manipulative), and Analysis Confidence (1=uncertain, 10=very confident).

**Reporter Agent** - The synthesizer. Creates a comprehensive markdown report combining all findings into a coherent narrative. Supports multilingual output (English and Polish), ensuring accessibility for diverse audiences.

## Why Multi-Agent Architecture?

The multi-agent approach provides four critical advantages over single-LLM systems:

**Specialization**: Each agent has a focused role with optimized prompts. The Researcher excels at fact-checking because that's its sole responsibility. The Analyst focuses entirely on manipulation detection. This specialization produces higher-quality analysis than asking one model to do everything.

**Cross-Validation**: The Critic agent independently validates all findings. When the Researcher cites a source, the Critic verifies its reliability. When the Analyst identifies a manipulation technique, the Critic challenges whether it's truly present. This adversarial review catches errors that a single LLM would miss.

**Tool Diversity**: Different agents use different tools. The Researcher uses Google Search for current events and real-time information. The Librarian uses Wikipedia for historical context and stable knowledge. This combination provides comprehensive coverage that no single tool can achieve.

**Emergent Intelligence**: Six specialized perspectives reveal patterns invisible to a single model. The sequential workflow builds understanding progressively: facts first, then context, then analysis, then critique, then scoring, then synthesis. The whole exceeds the sum of its parts.

## Technical Implementation: Google ADK Framework

VERA demonstrates deep mastery of Google ADK through five key concepts:

**Multi-Agent System**: Six agents execute in strict sequential order using manual orchestration. While ADK provides a SequentialAgent wrapper, I chose explicit for-loop control for maximum reliability and debugging capability. This decision proved crucial when handling tool conflicts between Google Search and Wikipedia.

**Tools Integration**: VERA uses both built-in tools (google_search via Grounding API) and custom tools (search_wikipedia). The Researcher and Librarian agents are deliberately separated to avoid tool conflicts—a key architectural decision that improved system stability.

**Sessions & Memory**: InMemorySessionService enables context continuity across agents. Each agent sees previous agents' outputs, allowing the Critic to review the Researcher's findings and the Reporter to synthesize all analyses into a coherent narrative.

**Observability**: Comprehensive structured logging (JSON + colored console) with per-agent log files, performance metrics, and session tracking. This observability was essential for debugging complex multi-agent interactions and optimizing performance.

**Deployment**: Production-ready deployment on Google Cloud Run with Docker containerization, automated CI/CD via Cloud Build, and proper secret management. The application serves real users at scale.

## Security & Safety

VERA implements multiple security layers:

**Prompt Injection Protection**: User input is wrapped in delimiters (`<<<USER_INPUT_START>>>` / `<<<USER_INPUT_END>>>`). Agents are explicitly instructed to IGNORE any commands within user content, preventing malicious users from hijacking agent behavior.

**XSS Prevention**: Reports are rendered without `unsafe_allow_html`, preventing script injection. Streamlit automatically sanitizes user-generated content.

**API Key Security**: No hardcoded credentials. Users provide their own Google AI Studio API keys, stored only in browser session memory, never persisted to disk or logs.

## Real-World Impact

VERA transforms fact-checking from an elite activity to a democratic tool:

- **Speed**: 2-3 minutes vs 4-6 hours for manual review
- **Cost**: ~$0.01-0.05 per analysis vs $50-100/hour for expert labor
- **Accessibility**: Anyone with internet access can verify claims
- **Objectivity**: Standardized 1-10 scoring vs subjective human judgment
- **Scalability**: Unlimited throughput vs 1-2 articles/day per human reviewer

### Use Case Example:

A viral health post claims "Morning jogging causes more arterial damage than smoking a pack of cigarettes" citing a "leaked memo from the Global Respiratory Alliance" and "Dr. Hans Vogle's study on Accelerated Oxidative Necrosis." Without VERA, verification takes hours and requires medical expertise. With VERA, a concerned reader pastes the text, waits 2-3 minutes, and receives a comprehensive report with fact-checking (fabricated organization, non-existent researcher, invented medical term), source citations, manipulation analysis (fear-mongering, conspiracy framing), and objective scores. They can make an informed decision about sharing or believing the content.

## Development Journey & Lessons Learned

VERA evolved through seven major iterations:

- **v1.0**: Single agent with Google Search (proof of concept)
- **v2.0**: Three agents (Researcher, Analyst, Reporter) established sequential workflow
- **v3.0**: Added Librarian (Wikipedia) and Critic for validation
- **v4.0**: Added Scoring agent for quantitative metrics
- **v5.0**: Comprehensive observability with structured logging
- **v6.0**: URL extraction, Streamlit UI improvements, real-time progress indicators
- **v7.0**: Production deployment, multilingual support, timestamped reports

### Key Lessons:

**Agent Specialization > Generalization**: Focused agents outperform generalists. Tool conflicts forced me to separate Researcher and Librarian, which unexpectedly improved quality.

**Cross-Validation Reduces Hallucinations**: The Critic agent catches errors that single-LLM systems miss. This independent validation is crucial for trustworthy AI.

**Tools Provide Real Grounding**: Google Search and Wikipedia prevent hallucinations by anchoring analysis in external facts. LLMs alone are prone to fabrication.

**Observability is Essential**: Multi-agent systems are complex. Without comprehensive logging, debugging would be impossible.

**User Experience Matters**: Real-time UI feedback, multilingual support, and clear disclaimers build trust and usability.

## Social Impact: Agents for Good

VERA embodies the "Agents for Good" mission by:

- **Democratizing Fact-Checking**: Making professional-grade analysis accessible to everyone, not just elite institutions
- **Promoting Media Literacy**: Teaching users to think critically about information sources and manipulation techniques
- **Protecting Public Health**: Enabling rapid verification of health claims during crises
- **Building Trust**: Providing transparent, source-cited analysis with clear confidence scores

VERA doesn't claim to be the ultimate truth arbiter—it explicitly warns users that it's a research tool requiring independent verification. But it empowers individuals to ask better questions, demand better sources, and resist manipulation.

## Conclusion

VERA demonstrates that multi-agent AI systems can tackle complex social challenges. By combining specialized agents, diverse tools, cross-validation, and thoughtful design, we can build AI that serves the public good. In an age of information overload and deliberate deception, VERA offers a path toward informed citizenship and democratic resilience.

The code is open source, the deployment is documented, and the impact is measurable. VERA proves that Google ADK enables developers to build not just impressive technical systems, but tools that make the world better.

---

## DISCLAIMER

**VERA is a research prototype. DO NOT use as sole basis for important decisions. Always verify critical information through authoritative sources. Use at your own risk.**
