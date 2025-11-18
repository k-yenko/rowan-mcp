# BioArena Discord Bot - Project & Folder Integration Plan

## Overview

Integrate Rowan MCP project and folder management into the BioArena Discord bot to organize battle workflows with a standardized hierarchy using Projects and Folders.

## Architecture

### Project + Folder Hierarchy

```
BioArena (PROJECT)
├── Home Folder (auto-created by project)
├── Structure Repository (auto-created by project)
├── battles-test (folder) ← Discord channel folder
│   ├── Battle #0001 (folder)
│   │   ├── Scientist 1, 2025-01-17 (subfolder)
│   │   │   └── [workflow submissions]
│   │   ├── Scientist 2, 2025-01-17 (subfolder)
│   │   └── Scientist 3, 2025-01-17 (subfolder)
│   └── Battle #0002 (folder)
├── battles-chemical-reasoning (folder) ← Discord channel folder
│   ├── Battle #0001 (folder)
│   └── Battle #0002 (folder)
├── battles-protein-folding (folder) ← Discord channel folder
│   └── Battle #0001 (folder)
└── battles-de-novo-binders (folder) ← Discord channel folder
    └── Battle #0001 (folder)
```

**Hierarchy Levels:**
1. **Project**: "BioArena" - Top-level container with access control and structure repository
2. **Channel Folders**: One folder per Discord channel (battles-test, battles-chemical-reasoning, etc.)
3. **Battle Folders**: Battle #XXXX within each channel folder
4. **Submission Folders**: Scientist X, YYYY-MM-DD within each battle

**Benefits:**
- Clear separation between different battle types (test, chemical reasoning, protein folding, etc.)
- Each Discord channel gets its own organized folder
- Easy to find battles by channel type
- Scalable as new battle channels are added

### Naming Conventions

- **Project**: `BioArena` (created once, stores project UUID in database)
- **Channel Folders**: Discord channel names (e.g., `battles-test`, `battles-chemical-reasoning`, `battles-protein-folding`, `battles-de-novo-binders`)
- **Battle Folders**: `Battle #XXXX` (zero-padded 4 digits, e.g., `Battle #0001`)
- **Submission Folders**: `Scientist X, YYYY-MM-DD` (e.g., `Scientist 3, 2025-01-17`)

### Database Schema Changes

Add new columns to existing tables:

```sql
-- Battles table
ALTER TABLE battles ADD COLUMN folder_uuid VARCHAR(255);
ALTER TABLE battles ADD COLUMN folder_url TEXT;
ALTER TABLE battles ADD COLUMN channel_name VARCHAR(255);  -- Discord channel name
ALTER TABLE battles ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Submissions table (or create if doesn't exist)
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    battle_id INTEGER REFERENCES battles(id),
    user_id VARCHAR(255) NOT NULL,  -- Discord user ID
    scientist_number INTEGER NOT NULL,  -- Per-battle scientist number
    folder_uuid VARCHAR(255) NOT NULL,
    folder_url TEXT,
    workflow_uuid VARCHAR(255),  -- NULL until workflow submitted
    workflow_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(battle_id, scientist_number)
);

-- Channel folders table
CREATE TABLE IF NOT EXISTS channel_folders (
    id SERIAL PRIMARY KEY,
    channel_name VARCHAR(255) UNIQUE NOT NULL,  -- Discord channel name
    folder_uuid VARCHAR(255) NOT NULL,
    folder_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Config table for project
CREATE TABLE IF NOT EXISTS bot_config (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT
);
-- Store project UUID: INSERT INTO bot_config VALUES ('bioarena_project_uuid', '<uuid>');
```

## Implementation

### 1. Setup & Initialization

**File**: `bot/services/folder_manager.py`

```python
"""
Rowan Project & Folder Management Service
Handles project and folder creation and organization for BioArena battles.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any
import rowan
from bot.database import db  # Your database connection


class FolderManager:
    """Manages Rowan project and folder creation and organization for battles."""

    def __init__(self):
        """Initialize folder manager with project UUID."""
        self.project_uuid = self._get_or_create_project()

    def _get_or_create_project(self) -> str:
        """Get BioArena project UUID from config, or create if missing.

        Returns:
            str: UUID of the "BioArena" project
        """
        # Check database for existing project
        result = db.execute(
            "SELECT value FROM bot_config WHERE key = 'bioarena_project_uuid'"
        ).fetchone()

        if result:
            return result[0]

        # Create project if doesn't exist
        project = rowan.create_project(name="BioArena")

        # Store in database
        db.execute(
            "INSERT INTO bot_config (key, value) VALUES ('bioarena_project_uuid', ?)",
            (project.uuid,)
        )
        db.commit()

        print(f"✓ Created BioArena project: {project.uuid}")
        print(f"  URL: https://labs.rowansci.com/project/{project.uuid}")
        print(f"  Includes: Home folder + Structure repository")

        return project.uuid

    def get_or_create_channel_folder(self, channel_name: str) -> str:
        """Get or create a folder for a Discord channel.

        Args:
            channel_name: Discord channel name (e.g., 'battles-test', 'battles-chemical-reasoning')

        Returns:
            str: UUID of the channel folder
        """
        # Check database for existing channel folder
        result = db.execute(
            "SELECT folder_uuid FROM channel_folders WHERE channel_name = ?",
            (channel_name,)
        ).fetchone()

        if result:
            return result[0]

        # Create channel folder if doesn't exist
        folder = rowan.create_folder(
            name=channel_name,
            parent_uuid=None,  # Will be created in default project's home folder
            notes=f"Parent folder for all battles in #{channel_name} Discord channel.",
            starred=True,  # Star for easy access
            public=True  # Always public
        )

        folder_uuid = folder.uuid
        folder_url = f"https://labs.rowansci.com/folder/{folder_uuid}"

        # Store in database
        db.execute(
            "INSERT INTO channel_folders (channel_name, folder_uuid, folder_url) VALUES (?, ?, ?)",
            (channel_name, folder_uuid, folder_url)
        )
        db.commit()

        print(f"✓ Created channel folder: {channel_name}")
        print(f"  UUID: {folder_uuid}")
        print(f"  URL: {folder_url}")

        return folder_uuid

    def create_battle_folder(
        self,
        battle_id: int,
        battle_number: int,
        channel_name: str
    ) -> Dict[str, str]:
        """Create a folder for a new battle within a channel folder.

        Args:
            battle_id: Database ID of the battle
            battle_number: Sequential battle number for display
            channel_name: Discord channel name (e.g., 'battles-test')

        Returns:
            Dictionary with folder_uuid and folder_url

        Example:
            >>> fm = FolderManager()
            >>> result = fm.create_battle_folder(
            ...     battle_id=42,
            ...     battle_number=1,
            ...     channel_name='battles-test'
            ... )
            >>> print(result)
            {'folder_uuid': 'abc-123', 'folder_url': 'https://labs.rowansci.com/folder/abc-123'}
        """
        folder_name = f"Battle #{battle_number:04d}"

        # Get or create channel folder first
        channel_folder_uuid = self.get_or_create_channel_folder(channel_name)

        try:
            folder = rowan.create_folder(
                name=folder_name,
                parent_uuid=channel_folder_uuid,  # Nested under channel folder
                notes=f"BioArena Battle #{battle_number} in #{channel_name}. All submissions for this battle are organized in subfolders.",
                starred=False,
                public=True  # Always public for transparency
            )

            folder_uuid = folder.uuid
            folder_url = f"https://labs.rowansci.com/folder/{folder_uuid}"

            # Update battle record in database
            db.execute(
                "UPDATE battles SET folder_uuid = ?, folder_url = ? WHERE id = ?",
                (folder_uuid, folder_url, battle_id)
            )
            db.commit()

            print(f"✓ Created battle folder: {folder_name}")
            print(f"  UUID: {folder_uuid}")
            print(f"  URL: {folder_url}")

            return {
                "folder_uuid": folder_uuid,
                "folder_url": folder_url
            }

        except Exception as e:
            print(f"✗ Failed to create battle folder: {e}")
            raise

    def create_submission_folder(
        self,
        battle_id: int,
        user_id: str,
        scientist_number: int
    ) -> Dict[str, Any]:
        """Create a submission folder for a user's challenge submission.

        Args:
            battle_id: Database ID of the battle
            user_id: Discord user ID
            scientist_number: Anonymized scientist number (per-battle)

        Returns:
            Dictionary with submission details

        Example:
            >>> fm = FolderManager()
            >>> result = fm.create_submission_folder(
            ...     battle_id=42,
            ...     user_id="123456789",
            ...     scientist_number=3
            ... )
            >>> print(result)
            {'submission_id': 5, 'folder_uuid': 'xyz-789', 'scientist_number': 3}
        """
        # Get battle folder UUID
        battle = db.execute(
            "SELECT folder_uuid FROM battles WHERE id = ?",
            (battle_id,)
        ).fetchone()

        if not battle or not battle[0]:
            raise ValueError(f"Battle {battle_id} has no folder assigned")

        battle_folder_uuid = battle[0]

        # Generate folder name with current date
        date_str = datetime.now().strftime("%Y-%m-%d")
        folder_name = f"Scientist {scientist_number}, {date_str}"

        try:
            folder = rowan.create_folder(
                name=folder_name,
                parent_uuid=battle_folder_uuid,  # Nested under battle folder
                notes=f"Submission by Scientist {scientist_number} for this battle.",
                starred=False,
                public=True  # Always public
            )

            folder_uuid = folder.uuid
            folder_url = f"https://labs.rowansci.com/folder/{folder_uuid}"

            # Create submission record
            db.execute(
                """INSERT INTO submissions
                   (battle_id, user_id, scientist_number, folder_uuid, folder_url)
                   VALUES (?, ?, ?, ?, ?)""",
                (battle_id, user_id, scientist_number, folder_uuid, folder_url)
            )
            db.commit()

            submission_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            print(f"✓ Created submission folder: {folder_name}")
            print(f"  UUID: {folder_uuid}")
            print(f"  URL: {folder_url}")

            return {
                "submission_id": submission_id,
                "folder_uuid": folder_uuid,
                "folder_url": folder_url,
                "scientist_number": scientist_number,
                "date": date_str
            }

        except Exception as e:
            print(f"✗ Failed to create submission folder: {e}")
            raise

    def get_next_scientist_number(self, battle_id: int) -> int:
        """Get the next available scientist number for a battle.

        Args:
            battle_id: Database ID of the battle

        Returns:
            Next scientist number (starts at 1)
        """
        result = db.execute(
            "SELECT MAX(scientist_number) FROM submissions WHERE battle_id = ?",
            (battle_id,)
        ).fetchone()

        max_number = result[0] if result[0] else 0
        return max_number + 1

    def assign_workflow_to_submission(
        self,
        submission_id: int,
        workflow_uuid: str
    ) -> None:
        """Assign a workflow to a submission folder.

        Args:
            submission_id: Database ID of the submission
            workflow_uuid: UUID of the workflow to assign
        """
        # Get submission folder UUID
        submission = db.execute(
            "SELECT folder_uuid FROM submissions WHERE id = ?",
            (submission_id,)
        ).fetchone()

        if not submission:
            raise ValueError(f"Submission {submission_id} not found")

        folder_uuid = submission[0]

        try:
            # Update workflow to be in the submission folder
            workflow = rowan.retrieve_workflow(workflow_uuid)
            workflow.update(parent_uuid=folder_uuid)

            workflow_url = f"https://labs.rowansci.com/workflow/{workflow_uuid}"

            # Update submission record
            db.execute(
                "UPDATE submissions SET workflow_uuid = ?, workflow_url = ? WHERE id = ?",
                (workflow_uuid, workflow_url, submission_id)
            )
            db.commit()

            print(f"✓ Assigned workflow {workflow_uuid} to submission {submission_id}")

        except Exception as e:
            print(f"✗ Failed to assign workflow: {e}")
            raise
```

### 2. Discord Bot Integration

**File**: `bot/cogs/battles.py`

```python
"""
Battle management commands for BioArena Discord bot.
"""

import discord
from discord.ext import commands
from bot.services.folder_manager import FolderManager
from bot.database import db


class BattlesCog(commands.Cog):
    """Commands for managing BioArena battles."""

    def __init__(self, bot):
        self.bot = bot
        self.folder_manager = FolderManager()

    @commands.command(name="create_battle")
    @commands.has_role("Admin")  # Restrict to admins
    async def create_battle(self, ctx, battle_name: str):
        """Create a new BioArena battle in the current channel.

        Usage: !create_battle "Protein Docking Challenge"
        """
        await ctx.send(f"🔄 Creating battle: **{battle_name}**...")

        try:
            # Get channel name from context
            channel_name = ctx.channel.name

            # Validate it's a battles channel
            if not channel_name.startswith("battles-"):
                await ctx.send("❌ Battles can only be created in #battles-* channels!")
                return

            # Get next battle number (per-channel or global - TBD)
            result = db.execute("SELECT MAX(battle_number) FROM battles").fetchone()
            next_battle_number = (result[0] or 0) + 1

            # Create battle in database
            db.execute(
                "INSERT INTO battles (name, battle_number, channel_name) VALUES (?, ?, ?)",
                (battle_name, next_battle_number, channel_name)
            )
            db.commit()

            battle_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            # Create Rowan folder for battle
            folder_info = self.folder_manager.create_battle_folder(
                battle_id=battle_id,
                battle_number=next_battle_number,
                channel_name=channel_name
            )

            embed = discord.Embed(
                title=f"✅ Battle Created: Battle #{next_battle_number:04d}",
                description=battle_name,
                color=discord.Color.green()
            )
            embed.add_field(
                name="Rowan Folder",
                value=f"[View Folder]({folder_info['folder_url']})",
                inline=False
            )
            embed.add_field(
                name="Battle ID",
                value=str(battle_id),
                inline=True
            )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Failed to create battle: {str(e)}")
            raise

    @commands.command(name="submit")
    async def submit_challenge(self, ctx, battle_id: int, smiles: str, *, options: str = ""):
        """Submit a challenge to a battle.

        Usage: !submit 1 "CCO" --workflow_type=solubility
        """
        await ctx.send(f"🔄 Processing your submission to Battle #{battle_id}...")

        try:
            user_id = str(ctx.author.id)

            # Check if user already submitted to this battle
            existing = db.execute(
                "SELECT id FROM submissions WHERE battle_id = ? AND user_id = ?",
                (battle_id, user_id)
            ).fetchone()

            if existing:
                await ctx.send("❌ You've already submitted to this battle!")
                return

            # Get next scientist number
            scientist_number = self.folder_manager.get_next_scientist_number(battle_id)

            # Create submission folder
            submission = self.folder_manager.create_submission_folder(
                battle_id=battle_id,
                user_id=user_id,
                scientist_number=scientist_number
            )

            # TODO: Submit workflow to Rowan (depends on workflow type)
            # For now, just create the folder structure

            embed = discord.Embed(
                title="✅ Submission Received",
                description=f"Your challenge has been submitted as **Scientist {scientist_number}**",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Battle",
                value=f"Battle #{battle_id}",
                inline=True
            )
            embed.add_field(
                name="Rowan Folder",
                value=f"[View Folder]({submission['folder_url']})",
                inline=False
            )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Submission failed: {str(e)}")
            raise


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(BattlesCog(bot))
```

### 3. Workflow Submission Integration

**File**: `bot/services/workflow_submitter.py`

```python
"""
Submit workflows to Rowan and assign to folders.
"""

import rowan
from typing import Dict, Any
from bot.services.folder_manager import FolderManager


class WorkflowSubmitter:
    """Handles workflow submission and folder assignment."""

    def __init__(self):
        self.folder_manager = FolderManager()

    def submit_and_assign(
        self,
        submission_id: int,
        workflow_type: str,
        smiles: str,
        **workflow_params
    ) -> Dict[str, Any]:
        """Submit a workflow and assign it to a submission folder.

        Args:
            submission_id: Database ID of the submission
            workflow_type: Type of workflow (e.g., 'solubility', 'pka', 'docking')
            smiles: SMILES string for the molecule
            **workflow_params: Additional workflow parameters

        Returns:
            Dictionary with workflow information
        """
        # Submit workflow based on type
        if workflow_type == "solubility":
            workflow = rowan.submit_solubility_workflow(
                smiles=smiles,
                name=f"Submission {submission_id}",
                **workflow_params
            )
        elif workflow_type == "pka":
            workflow = rowan.submit_pka_workflow(
                smiles=smiles,
                name=f"Submission {submission_id}",
                **workflow_params
            )
        # Add more workflow types as needed
        else:
            raise ValueError(f"Unsupported workflow type: {workflow_type}")

        workflow_uuid = workflow.uuid

        # Assign workflow to submission folder
        self.folder_manager.assign_workflow_to_submission(
            submission_id=submission_id,
            workflow_uuid=workflow_uuid
        )

        return {
            "workflow_uuid": workflow_uuid,
            "workflow_url": f"https://labs.rowansci.com/workflow/{workflow_uuid}",
            "status": "submitted"
        }
```

## Deployment Plan

### Phase 1: Database Setup
1. Run database migrations to add new tables/columns
2. Initialize bot_config table
3. Test database connections

### Phase 2: Folder Manager Implementation
1. Implement `FolderManager` class
2. Test root folder creation
3. Test battle folder creation
4. Test submission folder creation

### Phase 3: Discord Bot Integration
1. Implement `BattlesCog` commands
2. Test `!create_battle` command
3. Test `!submit` command
4. Add error handling and logging

### Phase 4: Workflow Integration
1. Implement `WorkflowSubmitter` class
2. Link workflow submission to folder assignment
3. Test end-to-end flow
4. Monitor for failures

## Error Handling

### Folder Creation Failures
```python
try:
    folder_info = self.folder_manager.create_battle_folder(battle_id, battle_number)
except rowan.exceptions.APIError as e:
    # Log to error channel
    await error_channel.send(f"⚠️ Rowan API error: {e}")
    # Retry with exponential backoff
    # Or fall back to default folder
except Exception as e:
    # Critical error - notify admins
    await admin_channel.send(f"🚨 Critical error creating battle folder: {e}")
    raise
```

### Database Transaction Safety
```python
try:
    # Start transaction
    db.execute("BEGIN TRANSACTION")

    # Create battle record
    db.execute("INSERT INTO battles ...")
    battle_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Create folder
    folder_info = folder_manager.create_battle_folder(battle_id, battle_number)

    # Commit only if both succeed
    db.commit()
except Exception as e:
    db.rollback()
    raise
```

## Testing Checklist

- [ ] Root folder creation on first run
- [ ] Root folder retrieval on subsequent runs
- [ ] Battle folder creation with correct naming
- [ ] Submission folder creation with correct scientist numbering
- [ ] Workflow assignment to submission folders
- [ ] Database integrity (foreign keys, unique constraints)
- [ ] Error handling for API failures
- [ ] Error handling for database failures
- [ ] Concurrent submissions (race conditions)
- [ ] Discord command permissions
- [ ] Embed formatting and URLs

## Future Enhancements

1. **Bulk Operations**: Create multiple battle folders at once
2. **Folder Archiving**: Move completed battles to archive folder
3. **Leaderboard Integration**: Pull workflow results from folders
4. **Folder Search**: Search submissions by scientist number or date
5. **Folder Analytics**: Track submission counts per battle
6. **Auto-numbering**: Automatically increment scientist numbers globally

## Why Projects + Folders?

### Benefits of Using Projects

1. **Access Control**: Projects have role-based permissions (Owner/Collaborator)
   - Easier to manage who can access BioArena battles
   - Can add collaborators without making individual folders/workflows public

2. **Structure Repository**: Automatic structure repository for reusable molecules
   - Save common ligands, proteins, solvents
   - Reuse structures across multiple battles without re-uploading

3. **Organization**: Clear separation between BioArena and personal research
   - All battle data in one dedicated project
   - Won't clutter personal default project

4. **Scalability**: Better for managing hundreds of battles
   - Project-level search and filtering
   - Easier to archive or export entire battle history

5. **Professional**: More appropriate for a competitive platform
   - Projects signal "this is a formal competition"
   - Folders alone might feel ad-hoc

### Implementation Notes

- **Project UUID**: Stored in `bot_config` table, created once on first bot startup
- **Battles Folder UUID**: Created within project, also stored in `bot_config`
- **All folders**: Created with `public=True` for transparency
- **Workflow assignment**: Use `parent_uuid` to place workflows in submission folders

## Questions to Resolve

1. ~~**Folder Hierarchy**~~ **RESOLVED: BioArena Project → Channel Folders → Battle Folders → Scientist Submissions**

2. **Battle Numbering**: Should battles be numbered:
   - **Per-channel** (each channel has Battle #0001, #0002, etc.), OR
   - **Globally** (Battle #0001 in battles-test, Battle #0002 in battles-chemical-reasoning, Battle #0003 in battles-test, etc.)?

3. **Scientist Numbering**: Per-battle or globally unique?
   - **Per-battle**: Each battle has Scientist 1, 2, 3, 4...
   - **Globally**: Scientist numbers increment across all battles

4. **Date Format**: `YYYY-MM-DD` or other format for submission folders?

5. **Workflow Types**: Which workflows are allowed in battles?
   - solubility, pka, docking, conformer_search, etc.?

6. **Database**: PostgreSQL, SQLite, or other?

7. **Multiple Submissions**: Can a scientist submit multiple workflows per battle?

8. **Project Sharing**: Should BioArena project be shared with admins/judges?

9. **Channel Folder Creation**: Should channel folders be:
   - **Pre-created** on bot startup, OR
   - **Auto-created** when first battle is posted to that channel?

10. **Channel Naming**: Use exact Discord names (`battles-test`) or prettier format (`Battles - Test`)?

---

**Author**: Claude Code
**Date**: 2025-01-17
**Status**: Updated - Using Projects + Folders
**Last Updated**: 2025-01-17 (Added Project Management)
