# Self-Healing Support Supervisor - Web UI

Production-ready Next.js dashboard for the Self-Healing Support Supervisor agentic AI system.

## Features

- **Dashboard**: Real-time overview of system status and agent loop
- **Signals**: Ingest new signals (OBSERVE phase)
- **Agent Analysis**: Run pattern detection and hypothesis formulation (REASON + DECIDE phases)
- **Actions**: Review and approve proposed actions with human-in-the-loop (ACT phase)
- **Explainability**: Full transparency into agent reasoning (EXPLAIN phase)
- **Incidents**: Track and manage open incidents
- **Knowledge Base**: Search long-term memory of resolved issues

## Tech Stack

- **Next.js 15** with App Router
- **React 19** with TypeScript
- **TailwindCSS** for styling
- **Fetch API** for backend communication

## Quick Start

### 1. Install Dependencies

```bash
cd ui
npm install
```

### 2. Configure Environment

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Backend

Make sure the FastAPI backend is running:

```bash
cd ..
python -m supervisor.api.server
```

### 4. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Production Build

```bash
npm run build
npm start
```

## Project Structure

```
ui/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard
│   ├── signals/           # Signal ingestion
│   ├── agent/             # Agent analysis
│   ├── actions/           # Action approval
│   ├── explain/           # Explainability
│   ├── incidents/         # Incident management
│   └── knowledge/         # Knowledge base
├── components/
│   ├── Layout.tsx         # Main layout with navigation
│   └── ui.tsx             # Shared UI components
└── lib/
    └── api.ts             # API client with TypeScript types
```

## Demo Workflow

1. **Ingest Signals** (`/signals`)
   - Submit test signals representing migration issues
   - Use checkout/auth-related scenarios for best demo

2. **Run Analysis** (`/agent`)
   - Set time window to 24 hours
   - Click "Run Agent Analysis"
   - Observe pattern detection and hypothesis formulation

3. **Review Actions** (`/actions`)
   - See proposed actions with safety warnings
   - Select actions to approve
   - Execute with human approval

4. **Understand Reasoning** (`/explain`)
   - Explore collapsible sections
   - See confidence justification
   - Understand why approval was required

5. **Track Incidents** (`/incidents`)
   - View open incidents
   - Monitor resolution status

6. **Search Knowledge** (`/knowledge`)
   - Search for patterns and solutions
   - See validation tracking

## Safety Features

- Clear human-in-the-loop controls
- Risk level indicators (LOW/MEDIUM/HIGH)
- Safety warnings for high-risk actions
- Full explainability for all decisions
- No auto-execution without approval

## Customization

### Update Backend URL

Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Styling

All components use TailwindCSS. Customize in `tailwind.config.ts` or component-level classes.

## Troubleshooting

### "Failed to fetch" errors

- Ensure backend is running at `http://localhost:8000`
- Check browser console for CORS issues
- Verify `.env.local` has correct API URL

### Build errors

```bash
rm -rf .next node_modules
npm install
npm run dev
```

## License

MIT
