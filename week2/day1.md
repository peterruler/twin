# Day 1: Introducing The Twin

## Your AI Digital Twin Comes to Life

Welcome to Week 2! This week, you'll build and deploy your own AI Digital Twin - a conversational AI that represents you (or anyone you choose) and can interact with visitors on your behalf. By the end of this week, your twin will be deployed on AWS, complete with memory, personality, and professional cloud infrastructure.

Today, we'll start by building a local version that showcases a fundamental challenge in AI applications: the importance of conversation memory.

## What You'll Learn Today

- **Next.js App Router** vs Pages Router architecture
- **Building a chat interface** with React and Tailwind CSS
- **Creating a FastAPI backend** for AI conversations
- **Understanding stateless AI** and why memory matters
- **Implementing file-based memory** for conversation persistence

## Understanding App Router vs Pages Router

In Week 1, we used Next.js with the **Pages Router**. This week, we're using the **App Router**. Here's what you need to know:

### Pages Router (Week 1)
- Files in `pages/` directory become routes
- `pages/index.tsx` → `/`
- `pages/product.tsx` → `/product`
- Uses `getServerSideProps` for data fetching

### App Router (Week 2)
- Files in `app/` directory define routes
- `app/page.tsx` → `/`
- `app/about/page.tsx` → `/about`
- Uses React Server Components by default
- More modern, better performance, recommended for new projects

For our purposes, the main difference is the project structure - the actual React code you write will be very similar!

## Part 1: Project Setup

### Step 1: Create Your Project Structure

Open Cursor (or your preferred IDE) and create a new project:

1. **Windows/Mac/Linux:** File → Open Folder → Create a new folder called `twin`
2. Open the `twin` folder in Cursor

### Step 2: Create Project Directories

In Cursor's file explorer (the left sidebar):

1. Right-click in the empty space under your `twin` folder
2. Select **New Folder** and name it `backend`
3. Right-click again and select **New Folder** and name it `memory`

Your project structure should now look like:
```
twin/
├── backend/
└── memory/
```

### Step 3: Initialize the Frontend

Let's create a Next.js app with the App Router.

Open a terminal in Cursor (Terminal → New Terminal or Ctrl+\` / Cmd+\`):

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
```

When prompted, accept all the default options by pressing Enter.

After it completes, create a components directory using Cursor's file explorer:

1. In the left sidebar, expand the `frontend` folder
2. Right-click on the `frontend` folder
3. Select **New Folder** and name it `components`

✅ **Checkpoint**: Your project structure should look like:
```
twin/
├── backend/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   └── (various config files)
└── memory/
```

## Part 2: Install Python Package Manager

We'll use `uv` - a modern, fast Python package manager that's much faster than pip.

### Install uv

Visit the uv installation guide: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

**Quick installation:**

**Mac/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, close and reopen your terminal, then verify:
```bash
uv --version
```

You should see a version number like `uv 0.8.18` or similar.

## Part 3: Create the Backend API

### Step 1: Create Requirements File

Create `backend/requirements.txt`:

```
fastapi
uvicorn
openai
python-dotenv
python-multipart
```

### Step 2: Create Environment Configuration

Create `backend/.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
CORS_ORIGINS=http://localhost:3000
```

Replace `your_openai_api_key_here` with your actual OpenAI API key from Week 1.

Remember to Save the file!

Also, it's a good practice in case you ever decide to push this repo to github:

1. Create a new file called .gitignore in the project root (twin)
2. Add a single line with ".env" in it
3. Save

### Step 3: Create Your Digital Twin's Personality

Create `backend/me.txt` with a description of who your digital twin represents. For example:

```
You are a chatbot acting as a "Digital Twin", representing [Your Name] on [Your Name]'s website,
and engaging with visitors to the website.

Your goal is to answer questions acting as [Your Name], to the best of your knowledge based on the 
provided context.

[Your Name] is a [your profession/role]. [Add 2-3 sentences about background, expertise, or interests].
```

Customize this to represent yourself or any persona you want your twin to embody!

### Step 4: Create the FastAPI Server (Without Memory)

Create `backend/server.py`:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Optional
import uuid

# Load environment variables
load_dotenv(override=True)

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI()


# Load personality details
def load_personality():
    with open("me.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


PERSONALITY = load_personality()


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
async def root():
    return {"message": "AI Digital Twin API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Create system message with personality
        # NOTE: No memory - each request is independent!
        messages = [
            {"role": "system", "content": PERSONALITY},
            {"role": "user", "content": request.message},
        ]

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=messages
        )

        return ChatResponse(
            response=response.choices[0].message.content, 
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Part 4: Create the Frontend Interface

### Step 1: Create the Twin Component

Create `frontend/components/twin.tsx`:

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export default function Twin() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string>('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: input,
                    session_id: sessionId || undefined,
                }),
            });

            if (!response.ok) throw new Error('Failed to send message');

            const data = await response.json();

            if (!sessionId) {
                setSessionId(data.session_id);
            }

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error:', error);
            // Add error message
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-50 rounded-lg shadow-lg">
            {/* Header */}
            <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white p-4 rounded-t-lg">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Bot className="w-6 h-6" />
                    AI Digital Twin
                </h2>
                <p className="text-sm text-slate-300 mt-1">Your AI course companion</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-gray-500 mt-8">
                        <Bot className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                        <p>Hello! I&apos;m your Digital Twin.</p>
                        <p className="text-sm mt-2">Ask me anything about AI deployment!</p>
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex gap-3 ${
                            message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                    >
                        {message.role === 'assistant' && (
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                                    <Bot className="w-5 h-5 text-white" />
                                </div>
                            </div>
                        )}

                        <div
                            className={`max-w-[70%] rounded-lg p-3 ${
                                message.role === 'user'
                                    ? 'bg-slate-700 text-white'
                                    : 'bg-white border border-gray-200 text-gray-800'
                            }`}
                        >
                            <p className="whitespace-pre-wrap">{message.content}</p>
                            <p
                                className={`text-xs mt-1 ${
                                    message.role === 'user' ? 'text-slate-300' : 'text-gray-500'
                                }`}
                            >
                                {message.timestamp.toLocaleTimeString()}
                            </p>
                        </div>

                        {message.role === 'user' && (
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                                    <User className="w-5 h-5 text-white" />
                                </div>
                            </div>
                        )}
                    </div>
                ))}

                {isLoading && (
                    <div className="flex gap-3 justify-start">
                        <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                        </div>
                        <div className="bg-white border border-gray-200 rounded-lg p-3">
                            <div className="flex space-x-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-gray-200 p-4 bg-white rounded-b-lg">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder="Type your message..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-600 focus:border-transparent text-gray-800"
                        disabled={isLoading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={!input.trim() || isLoading}
                        className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
```

### Step 2: Install Required Dependencies

The Twin component uses lucide-react for icons. Install it:

```bash
cd frontend
npm install lucide-react
cd ..
```

### Step 3: Update the Main Page

Replace the contents of `frontend/app/page.tsx`:

```typescript
import Twin from '@/components/twin';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
            AI in Production
          </h1>
          <p className="text-center text-gray-600 mb-8">
            Deploy your Digital Twin to the cloud
          </p>

          <div className="h-[600px]">
            <Twin />
          </div>

          <footer className="mt-8 text-center text-sm text-gray-500">
            <p>Week 2: Building Your Digital Twin</p>
          </footer>
        </div>
      </div>
    </main>
  );
}
```

### Step 4: Fix Tailwind v4 Configuration

Next.js 15.5 comes with Tailwind CSS v4, which has a different configuration approach. We need to update two files:

First, update `frontend/postcss.config.mjs`:

```javascript
export default {
    plugins: {
        '@tailwindcss/postcss': {},
    },
}
```

### Step 5: Update Global Styles for Tailwind v4

Replace the contents of `frontend/app/globals.css`:

```css
@import 'tailwindcss';

/* Smooth scrolling animation keyframe */
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
}

.animate-bounce {
  animation: bounce 1.4s infinite;
}

.delay-100 {
  animation-delay: 0.1s;
}

.delay-200 {
  animation-delay: 0.2s;
}
```

## Part 5: Test Your Digital Twin (Without Memory)

### Step 1: Start the Backend Server

Open a new terminal in Cursor (Terminal → New Terminal):

```bash
cd backend
uv init --bare
uv python pin 3.12
uv add -r requirements.txt
uv run uvicorn server:app --reload
```

You should see something like this at the end:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 2: Start the Frontend Development Server

Open another new terminal:

```bash
cd frontend
npm run dev
```

You should see:
```
▲ Next.js 15.x.x
Local: http://localhost:3000
```

### Step 3: Experience the Memory Problem

1. Open your browser and go to `http://localhost:3000`
2. You should see your Digital Twin interface
3. Try this conversation:
   - **You:** "Hi! My name is Alex"
   - **Twin:** (responds with a greeting)
   - **You:** "What's my name?"
   - **Twin:** (won't remember your name!)

**What's happening?** Your twin has no memory! Each message is processed independently with no context from previous messages. This is like meeting someone new every single time you talk to them.

## Part 6: Adding Memory to Your Twin

Now let's fix this by adding conversation memory that persists to files.

### Step 1: Update the Backend with Memory Support

Replace your `backend/server.py` with this enhanced version:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict
import json
import uuid
from datetime import datetime
from pathlib import Path

# Load environment variables
load_dotenv(override=True)

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI()

# Memory directory
MEMORY_DIR = Path("../memory")
MEMORY_DIR.mkdir(exist_ok=True)


# Load personality details
def load_personality():
    with open("me.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


PERSONALITY = load_personality()


# Memory functions
def load_conversation(session_id: str) -> List[Dict]:
    """Load conversation history from file"""
    file_path = MEMORY_DIR / f"{session_id}.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_conversation(session_id: str, messages: List[Dict]):
    """Save conversation history to file"""
    file_path = MEMORY_DIR / f"{session_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
async def root():
    return {"message": "AI Digital Twin API with Memory"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Load conversation history
        conversation = load_conversation(session_id)
        
        # Build messages with history
        messages = [{"role": "system", "content": PERSONALITY}]
        
        # Add conversation history
        for msg in conversation:
            messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        assistant_response = response.choices[0].message.content
        
        # Update conversation history
        conversation.append({"role": "user", "content": request.message})
        conversation.append({"role": "assistant", "content": assistant_response})
        
        # Save updated conversation
        save_conversation(session_id, conversation)
        
        return ChatResponse(
            response=assistant_response,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def list_sessions():
    """List all conversation sessions"""
    sessions = []
    for file_path in MEMORY_DIR.glob("*.json"):
        session_id = file_path.stem
        with open(file_path, "r", encoding="utf-8") as f:
            conversation = json.load(f)
            sessions.append({
                "session_id": session_id,
                "message_count": len(conversation),
                "last_message": conversation[-1]["content"] if conversation else None
            })
    return {"sessions": sessions}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 2: Restart the Backend Server

Stop the backend server (Ctrl+C in the terminal) and restart it:

```bash
uv run uvicorn server:app --reload
```

### Step 3: Test Memory Persistence

1. Refresh your browser at `http://localhost:3000`
2. Have a conversation:
   - **You:** "Hi! My name is Alex and I love Python"
   - **Twin:** (responds with greeting)
   - **You:** "What's my name and what do I love?"
   - **Twin:** (remembers your name is Alex and you love Python!)

3. Check the memory folder - you'll see JSON files containing your conversations!

```bash
ls ../memory/
```

You'll see files like `abc123-def456-....json` containing the full conversation history.

## Understanding What We Built

### The Architecture

```
User Browser → Next.js Frontend → FastAPI Backend → OpenAI API
                     ↑                    ↓
                     └──── Memory Files ←─┘
```

### Key Components

1. **Frontend (Next.js with App Router)**
   - `app/page.tsx`: Main page using Server Components
   - `components/twin.tsx`: Client-side chat component
   - Real-time UI updates with React state

2. **Backend (FastAPI)**
   - RESTful API endpoints
   - OpenAI integration
   - File-based memory persistence
   - Session management

3. **Memory System**
   - JSON files store conversation history
   - Each session has its own file
   - Conversations persist across server restarts

## Congratulations! 🎉

You've successfully built your first AI Digital Twin with:
- ✅ A responsive chat interface
- ✅ Integration with OpenAI's API
- ✅ Persistent conversation memory
- ✅ Session management
- ✅ Professional project structure

### What You've Learned

1. **The importance of memory in AI applications** - Without memory, AI interactions feel disconnected and frustrating
2. **File-based persistence** - A simple but effective way to store conversation history
3. **Session management** - How to track different conversations
4. **Full-stack AI development** - Connecting frontend, backend, and AI services

## Troubleshooting

### "Connection refused" error
- Make sure both backend and frontend servers are running
- Check that the backend is on port 8000 and frontend on port 3000

### OpenAI API errors
- Verify your API key is correct in `backend/.env`
- Check you have credits in your OpenAI account

### Memory not persisting
- Ensure the `memory/` directory exists
- Check file permissions if on Linux/Mac
- Look for `.json` files in the memory directory

### Frontend not updating
- Clear your browser cache
- Make sure you saved all files
- Check the browser console for errors

## Next Steps

Tomorrow (Day 2), we'll:
- Add personalization with custom data and documents
- Deploy the backend to AWS Lambda
- Set up CloudFront for global distribution
- Create a production-ready architecture

Your Digital Twin is just getting started! Tomorrow we'll give it more personality and deploy it to the cloud.

## Resources

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [uv Documentation](https://docs.astral.sh/uv/)

Ready for Day 2? Your twin is about to get a lot more interesting! 🚀