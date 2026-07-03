import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Upload, Layers, History, Moon, Sun } from 'lucide-react';

import Home from './pages/Home';
import Results from './pages/Results';

const queryClient = new QueryClient();

function App() {
  const [darkMode, setDarkMode] = useState(true);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className={`min-h-screen ${darkMode ? 'dark' : ''} bg-background text-foreground flex flex-col`}>
        <Router>
          <header className="border-b border-border bg-card">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="h-6 w-6 text-blue-500" />
                <span className="font-bold text-xl tracking-tight">AI Inspect</span>
              </div>
              <nav className="flex items-center gap-6">
                <Link to="/" className="flex items-center gap-2 text-sm font-medium hover:text-blue-500 transition-colors">
                  <Upload className="h-4 w-4" /> Compare
                </Link>
                <Link to="/" className="flex items-center gap-2 text-sm font-medium hover:text-blue-500 transition-colors text-muted-foreground">
                  <History className="h-4 w-4" /> History
                </Link>
                <button onClick={toggleDarkMode} className="p-2 rounded-full hover:bg-muted transition-colors">
                  {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </button>
              </nav>
            </div>
          </header>

          <main className="flex-1 container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/results/:id" element={<Results />} />
            </Routes>
          </main>
        </Router>
      </div>
    </QueryClientProvider>
  );
}

export default App;
