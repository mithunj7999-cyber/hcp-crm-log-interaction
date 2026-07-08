import React from 'react';
import LeftPanelForm from './components/LeftPanelForm';
import RightPanelChat from './components/RightPanelChat';
import './App.css';

export default function App() {
  return (
    <div className="app-container">
      <LeftPanelForm />
      <RightPanelChat />
    </div>
  );
}
