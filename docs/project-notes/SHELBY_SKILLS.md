# Shelby Protocol Skills for Claude Code

A complete suite of 4 specialized Claude Code skills for working with the Shelby Protocol - a decentralized blob storage network built on Aptos blockchain.

## 🎯 What Was Created

Four production-ready Claude Code skills covering the entire Shelby Protocol ecosystem:

### 1. **shelby-quickstart**
Complete onboarding skill for first-time users
- Initial setup and configuration
- Token system explanation
- Path selection (CLI/SDK/Player)
- First upload walkthrough
- Next steps guidance

### 2. **shelby-cli-helper**
Expert CLI operations and troubleshooting
- Installation and configuration
- File upload/download operations
- Account management and funding
- Error troubleshooting
- Automation and scripting

### 3. **shelby-sdk-integration**
TypeScript SDK integration for Node.js and browser
- SDK setup for Node.js and browser
- Aptos authentication
- Blob upload patterns
- Error handling
- Production best practices

### 4. **shelby-media-player**
React video player integration
- SimpleShakaVideoPlayer setup
- TailwindCSS 4 configuration
- Custom player layouts
- Shelby storage integration
- Advanced customization

## 📁 File Structure

```
.claude/skills/
├── README.md                           # Main overview and guide
├── shelby-quickstart/
│   ├── SKILL.md                       # Main skill (3,020 lines)
│   └── README.md                      # Skill documentation
├── shelby-cli-helper/
│   ├── SKILL.md                       # Main skill (2,520 lines)
│   └── README.md                      # Skill documentation
├── shelby-sdk-integration/
│   ├── SKILL.md                       # Main skill (4,003 lines)
│   └── README.md                      # Skill documentation
└── shelby-media-player/
    ├── SKILL.md                       # Main skill (5,233 lines)
    └── README.md                      # Skill documentation
```

## 🚀 Installation

### Option 1: Use in This Project (Already Installed)
Skills are already in `.claude/skills/` and ready to use!

Just restart Claude Code to load them.

### Option 2: Copy to Another Project
```bash
# Copy all Shelby skills
cp -r .claude/skills/shelby-* /path/to/your/project/.claude/skills/

# Or copy individually
cp -r .claude/skills/shelby-quickstart /path/to/your/project/.claude/skills/
cp -r .claude/skills/shelby-cli-helper /path/to/your/project/.claude/skills/
cp -r .claude/skills/shelby-sdk-integration /path/to/your/project/.claude/skills/
cp -r .claude/skills/shelby-media-player /path/to/your/project/.claude/skills/
```

### Option 3: Install Globally (Personal Use)
```bash
# Copy to personal skills directory
mkdir -p ~/.claude/skills
cp -r .claude/skills/shelby-* ~/.claude/skills/
```

## ✅ Verification

After installation, restart Claude Code and verify:

```bash
# Check skills loaded
/skills
```

You should see:
- ✅ shelby-quickstart
- ✅ shelby-cli-helper
- ✅ shelby-sdk-integration
- ✅ shelby-media-player

## 🧪 Testing Skills

Test each skill with these prompts:

```
# Test 1: Quickstart
"I'm new to Shelby. How do I get started?"

# Test 2: CLI Helper
"How do I upload a video file to Shelby using the CLI?"

# Test 3: SDK Integration
"Set up Shelby SDK in my Node.js application to upload files"

# Test 4: Media Player
"Create a React video player component to stream from Shelby storage"
```

## 📚 Skill Features

### Auto-Invocation Triggers

Each skill has carefully crafted descriptions to trigger automatically:

**shelby-quickstart** triggers on:
- "get started with Shelby"
- "Shelby setup"
- "new to Shelby"
- "Shelby onboarding"

**shelby-cli-helper** triggers on:
- "shelby upload"
- "shelby CLI"
- "Shelby command line"
- "upload to Shelby"

**shelby-sdk-integration** triggers on:
- "@shelby-protocol/sdk"
- "ShelbyNodeClient"
- "Shelby SDK"
- "programmatic Shelby"

**shelby-media-player** triggers on:
- "@shelby-protocol/player"
- "SimpleShakaVideoPlayer"
- "Shelby video player"
- "video streaming Shelby"

### Comprehensive Coverage

Each skill includes:
- ✅ Clear purpose and use cases
- ✅ Step-by-step processes
- ✅ Complete code examples
- ✅ Error handling guidance
- ✅ Best practices
- ✅ Troubleshooting section
- ✅ Related resources
- ✅ Cross-references to other skills

### Production-Ready Examples

All skills include:
- ✅ TypeScript examples with full imports
- ✅ Error handling patterns
- ✅ Security best practices
- ✅ Real-world use cases
- ✅ Integration patterns
- ✅ Testing guidance

## 🎓 Usage Guide

### For Complete Beginners
1. Start with: `shelby-quickstart`
2. Follow the CLI path for easiest onboarding
3. Use `shelby-cli-helper` for ongoing work

### For Backend Developers
1. Review: `shelby-quickstart` (overview)
2. Primary: `shelby-sdk-integration` (Node.js)
3. Reference: `shelby-cli-helper` (manual uploads)

### For Frontend Developers
1. Start: `shelby-quickstart` (basics)
2. Primary: `shelby-media-player` (React player)
3. Optional: `shelby-sdk-integration` (browser uploads)

### For Full-Stack Teams
1. Onboarding: `shelby-quickstart`
2. DevOps: `shelby-cli-helper`
3. Backend: `shelby-sdk-integration`
4. Frontend: `shelby-media-player`

## 📖 Documentation

### Skill Documentation
- [Main README](./.claude/skills/README.md) - Complete overview
- [shelby-quickstart](./.claude/skills/shelby-quickstart/README.md)
- [shelby-cli-helper](./.claude/skills/shelby-cli-helper/README.md)
- [shelby-sdk-integration](./.claude/skills/shelby-sdk-integration/README.md)
- [shelby-media-player](./.claude/skills/shelby-media-player/README.md)

### Source Documentation
Skills built from official docs at:
- [Shelby Overview](./docs/shelby/overview.md)
- [CLI Guide](./docs/shelby/cli-guide.md)
- [TypeScript SDK](./docs/shelby/typescript-sdk.md)
- [Media Player](./docs/shelby/media-player.md)
- [API Reference](./docs/shelby/api-reference.md)
- [Explorer](./docs/shelby/explorer.md)

### Official Resources
- **Website**: https://shelby.xyz
- **Documentation**: https://docs.shelby.xyz
- **Explorer**: https://explorer.shelby.xyz
- **Whitepaper**: https://shelby.xyz/whitepaper.pdf

## 🛠️ Technical Details

### Tools Used
- Built with: `skill-builder` skill
- Following: Claude Code best practices
- Based on: Official Shelby documentation (2025-11-06)

### Skill Configuration
Each skill uses:
```yaml
name: skill-name
description: Detailed description with WHAT and WHEN
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
```

### Model Selection
All skills use `model: sonnet` for:
- Balanced performance and capability
- Efficient token usage
- Production-ready responses

### Tool Access
Skills have appropriate tool restrictions:
- **CLI helper**: Includes Bash for commands
- **SDK/Player**: Focused on Read, Write, Edit
- **All**: Grep, Glob for code exploration

## 🎯 Example Workflows

### Workflow 1: First Upload
```
User → "I want to upload a video to Shelby"
↓
shelby-quickstart → Guides through setup
↓
shelby-cli-helper → Provides upload command
↓
Success!
```

### Workflow 2: Build Video Platform
```
User → "Build a video streaming platform with Shelby"
↓
shelby-quickstart → Ecosystem overview
↓
shelby-cli-helper → Manual testing uploads
↓
shelby-sdk-integration → Backend upload service
↓
shelby-media-player → Frontend player components
↓
Complete platform!
```

### Workflow 3: Automate Uploads
```
User → "Automate video uploads to Shelby"
↓
shelby-cli-helper → CLI automation with bash
↓
shelby-sdk-integration → Node.js service
↓
Automated pipeline!
```

## 📊 Skill Statistics

| Skill | Lines | Features | Examples |
|-------|-------|----------|----------|
| shelby-quickstart | 3,020 | 7 paths | 3 detailed |
| shelby-cli-helper | 2,520 | 5 operations | 4 scenarios |
| shelby-sdk-integration | 4,003 | 6 patterns | 3 complete |
| shelby-media-player | 5,233 | 6 components | 3 advanced |
| **Total** | **14,776** | **24** | **13** |

## 🎨 Skill Quality

Each skill includes:
- ✅ Comprehensive YAML frontmatter
- ✅ Detailed "When to Use" triggers
- ✅ Step-by-step processes
- ✅ Multiple complete examples
- ✅ Error handling sections
- ✅ Best practices guides
- ✅ Troubleshooting help
- ✅ Related resources
- ✅ Cross-skill references
- ✅ Production patterns

## 🔗 Skill Relationships

```
shelby-quickstart (Entry Point)
    ├─→ shelby-cli-helper (CLI Path)
    ├─→ shelby-sdk-integration (SDK Path)
    └─→ shelby-media-player (Media Path)

shelby-cli-helper
    └─→ shelby-sdk-integration (Automation alternative)

shelby-sdk-integration
    └─→ shelby-media-player (Frontend integration)

shelby-media-player
    └─→ shelby-sdk-integration (Upload videos)
```

## 💡 Pro Tips

1. **Start Simple**: Always begin with `shelby-quickstart`
2. **CLI First**: Even SDK users benefit from CLI understanding
3. **Test Locally**: Use small files for initial testing
4. **Security**: Never commit private keys or credentials
5. **Monitor Balances**: Check tokens before large uploads
6. **Use Explorer**: Verify uploads at https://explorer.shelby.xyz

## 🐛 Troubleshooting

### Skills Not Loading
```bash
# Check skill files exist
ls -la .claude/skills/shelby-*

# Restart Claude Code
# Skills load at startup
```

### Skills Not Auto-Invoking
```bash
# Test with explicit invocation
"Use the shelby-quickstart skill to help me get started"

# Check skill descriptions match your query
cat .claude/skills/shelby-quickstart/SKILL.md | grep "description:"
```

### Need Different Skill
Each skill references related skills:
- Check "Related Skills" section
- Use cross-references
- Start with `shelby-quickstart` if unsure

## 📝 Updates and Maintenance

To update skills:
1. Edit `SKILL.md` files
2. Update `README.md` if needed
3. Restart Claude Code
4. Test with example prompts

## 🙏 Credits

- **Built with**: skill-builder skill for Claude Code
- **Based on**: Official Shelby Protocol documentation
- **Documentation source**: https://docs.shelby.xyz (2025-11-06)
- **Shelby Protocol**: https://shelby.xyz

## 📄 License

These skills are provided as educational resources for working with the Shelby Protocol.

---

**Ready to use!** 🚀

Restart Claude Code and start with:
```
"I'm new to Shelby. How do I get started?"
```
