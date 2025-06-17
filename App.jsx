import React, { useEffect, useState } from 'react';
import ChatPanel from './ChatPanel';
import RightPanel from './RightPanel';
import LeftPanel from './LeftPanel';

function App() {
  const [thought, setThought] = useState('');
  const [tip, setTip] = useState('');
  const [moodStats, setMoodStats] = useState({});
  const userId = "user123"; // Replace with actual auth/userID

  useEffect(() => {
    fetch('/daily_thought').then(res => res.json()).then(data => setThought(data.thought));
    fetch('/healthy_tip').then(res => res.json()).then(data => setTip(data.tip));
    fetch(`/mood_stats/${userId}`).then(res => res.json()).then(data => setMoodStats(data));
  }, []);

  return (
    <div className="app-container">
      <LeftPanel moodStats={moodStats} healthyTip={tip} />
      <ChatPanel userId={userId} />
      <RightPanel dailyThought={thought} />
    </div>
  );
}

export default App;
