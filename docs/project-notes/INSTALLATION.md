# Shelby Protocol Skills - Installation & Quick Start

## ✅ What's Included

Four complete Claude Code skills for the Shelby Protocol:

1. **shelby-quickstart** (585 lines) - First-time setup and onboarding
2. **shelby-cli-helper** (275 lines) - CLI operations and troubleshooting  
3. **shelby-sdk-integration** (535 lines) - TypeScript SDK integration
4. **shelby-media-player** (601 lines) - React video player components

**Total: 1,996 lines of skill content + 204 lines of documentation**

## 🚀 Quick Start

### Step 1: Verify Installation

Skills are already installed in this project at:
```
.claude/skills/shelby-quickstart/
.claude/skills/shelby-cli-helper/
.claude/skills/shelby-sdk-integration/
.claude/skills/shelby-media-player/
```

### Step 2: Restart Claude Code

Skills load at startup. Restart to activate.

### Step 3: Test a Skill

Try this prompt:
```
I'm new to Shelby. How do I get started?
```

The `shelby-quickstart` skill should activate automatically and guide you through setup.

## 📋 All Test Prompts

```bash
# Test shelby-quickstart
"I'm new to Shelby. How do I get started?"

# Test shelby-cli-helper  
"How do I upload a video file to Shelby using the CLI?"

# Test shelby-sdk-integration
"Set up Shelby SDK in my Node.js application"

# Test shelby-media-player
"Create a React video player component for Shelby storage"
```

## 📁 Skill Files

Each skill has:
- `SKILL.md` - Main skill definition with YAML frontmatter
- `README.md` - Quick reference documentation

Plus:
- `.claude/skills/README.md` - Complete overview of all skills
- `SHELBY_SKILLS.md` - This installation guide
- `docs/shelby/` - Source documentation

## 🎯 Choose Your Path

### Path A: Complete Beginner
Start → `shelby-quickstart` → Follow CLI path → Use `shelby-cli-helper`

### Path B: Backend Developer  
Start → `shelby-quickstart` → Use `shelby-sdk-integration` → Reference `shelby-cli-helper`

### Path C: Frontend Developer
Start → `shelby-quickstart` → Use `shelby-media-player` → Optional `shelby-sdk-integration`

### Path D: Full-Stack Team
All skills! Start with `shelby-quickstart` for onboarding.

## 📚 Documentation

- **Main README**: `.claude/skills/README.md`
- **This Guide**: `SHELBY_SKILLS.md`
- **Source Docs**: `docs/shelby/*.md`
- **Official**: https://docs.shelby.xyz

## 🔧 Copy to Other Projects

```bash
# Copy all skills
cp -r .claude/skills/shelby-* /path/to/project/.claude/skills/

# Or install globally
cp -r .claude/skills/shelby-* ~/.claude/skills/
```

## ✨ Features

- ✅ Auto-invocation via keyword triggers
- ✅ Comprehensive error handling
- ✅ Production-ready code examples
- ✅ Step-by-step processes
- ✅ Best practices guidance
- ✅ Cross-skill references
- ✅ TypeScript examples
- ✅ Security recommendations

## 🎓 What You Can Do

After using these skills, you'll know how to:
- Upload files to Shelby decentralized storage
- Build video streaming applications
- Integrate Shelby SDK into Node.js/browser apps
- Create custom React video players
- Automate uploads with CLI/SDK
- Handle errors and troubleshoot issues
- Follow security best practices
- Deploy production applications

## 🚀 Ready!

You're all set. Restart Claude Code and start with:

```
I'm new to Shelby. How do I get started?
```

Happy building! 🎉
