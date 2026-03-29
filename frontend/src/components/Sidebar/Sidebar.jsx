import React, { useEffect, useState } from "react";
import { getAllSessions, deleteSession, updateSessionFolder, getAllFolders, createFolder, deleteFolder } from "../../api/sessions";
import "./Sidebar.css";

export default function Sidebar({ currentSessionId, onLoadSession, onCreateSession, isStreaming }) {
  const [sessions, setSessions] = useState([]);
  const [folders, setFolders] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false); // Mobile toggle state
  const [isAddingFolder, setIsAddingFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [sessData, fldsData] = await Promise.all([
        getAllSessions(),
        getAllFolders()
      ]);
      setSessions(sessData);
      setFolders(fldsData);
    } catch (e) {
      console.error("Failed to fetch sidebar data", e);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch immediately and poll every 10 seconds or when a session completes
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  // When stream ends, refresh to get new title
  useEffect(() => {
    if (!isStreaming) {
      setTimeout(fetchData, 500);
    }
  }, [isStreaming]);

  const handleCreate = () => {
    onCreateSession();
    setIsOpen(false);
  };

  const handleLoad = (id) => {
    onLoadSession(id);
    setIsOpen(false);
  };

  const handleDeleteSession = async (e, id) => {
    e.stopPropagation();
    try {
       await deleteSession(id);
       await fetchData();
       if (currentSessionId === id) onCreateSession();
    } catch (err) { console.error(err); }
  };

  const handleCreateFolder = async (e) => {
    e.preventDefault();
    if (!newFolderName.trim()) {
      setIsAddingFolder(false);
      return;
    }
    try {
      await createFolder(newFolderName.trim());
      setNewFolderName("");
      setIsAddingFolder(false);
      await fetchData();
    } catch (err) { console.error(err); }
  };

  const handleDeleteFolder = async (e, id) => {
    e.stopPropagation();
    const deleteSessions = window.confirm("Delete all conversations inside this folder too?");
    try {
      await deleteFolder(id, deleteSessions);
      await fetchData();
    } catch (err) { console.error(err); }
  };

  const handleDropToFolder = async (folderId, e) => {
    e.preventDefault();
    e.stopPropagation();
    const sessionId = e.dataTransfer.getData("sessionId");
    if (!sessionId) return;
    try {
      await updateSessionFolder(sessionId, folderId);
      await fetchData();
    } catch (err) { console.error(err); }
  };

  const allowDrop = (e) => e.preventDefault();

  const groupSessions = (sessions) => {
    const groups = {
      Today: [],
      Yesterday: [],
      'Previous 7 Days': [],
      'Previous 30 Days': [],
      Older: []
    };

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const yesterday = today - 86400000;
    const past7Days = today - 86400000 * 7;
    const past30Days = today - 86400000 * 30;

    // Separate uncategorized sessions vs mapped to folders
    const uncategorizedSessions = sessions.filter(s => !s.folder_id);
    const folderSessions = {};
    folders.forEach(f => folderSessions[f.id] = []);
    
    sessions.forEach(s => {
      if (s.folder_id && folderSessions[s.folder_id]) {
        folderSessions[s.folder_id].push(s);
      }
    });

    uncategorizedSessions.forEach(s => {
      const ms = s.created_at * 1000;
      if (ms >= today) groups.Today.push(s);
      else if (ms >= yesterday) groups.Yesterday.push(s);
      else if (ms >= past7Days) groups['Previous 7 Days'].push(s);
      else if (ms >= past30Days) groups['Previous 30 Days'].push(s);
      else groups.Older.push(s);
    });

    return { groups, folderMap: folderSessions };
  };

  const { groups: groupedSessions, folderMap } = groupSessions(sessions);

  const renderSessionItem = (s) => (
    <button
      key={s.session_id}
      className={`session-item ${s.session_id === currentSessionId ? "active" : ""}`}
      onClick={() => handleLoad(s.session_id)}
      disabled={isStreaming}
      draggable
      onDragStart={(e) => e.dataTransfer.setData("sessionId", s.session_id)}
    >
      <div className="session-item-content">
        <div className="session-item-title">{s.title || "New Conversation"}</div>
        <div className="session-actions" onClick={(e) => handleDeleteSession(e, s.session_id)}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6"/></svg>
        </div>
      </div>
    </button>
  );

  return (
    <>
      {/* Mobile Toggle Overlay/Button logic could go here, omitting for simplicity desktop-first */}
      <aside className={`app-sidebar ${isOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <button 
            className="btn btn-primary new-chat-btn" 
            onClick={handleCreate}
            disabled={isStreaming}
          >
            + New Chat
          </button>
        </div>

        <div className="sidebar-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Folders & History</span>
          <button 
            className="btn btn-ghost"
            style={{ padding: '2px 6px', fontSize: '12px' }}
            onClick={() => setIsAddingFolder(!isAddingFolder)}
          >
            + Folder
          </button>
        </div>

        <div className="sidebar-sessions" onDragOver={allowDrop} onDrop={(e) => handleDropToFolder(null, e)}>
          {isAddingFolder && (
            <form onSubmit={handleCreateFolder} className="sidebar-group new-folder-form">
              <input 
                autoFocus
                className="chat-input"
                style={{ padding: '6px', fontSize: '0.8rem', width: '100%', marginBottom: '8px' }}
                placeholder="Folder name..."
                value={newFolderName}
                onChange={e => setNewFolderName(e.target.value)}
                onBlur={() => !newFolderName && setIsAddingFolder(false)}
              />
            </form>
          )}

          {folders.map(folder => (
            <div 
              key={folder.id} 
              className="sidebar-group folder-group"
              onDragOver={allowDrop}
              onDrop={(e) => handleDropToFolder(folder.id, e)}
            >
              <div className="sidebar-group-title folder-title">
                <span>📁 {folder.name}</span>
                <span className="folder-actions" onClick={(e) => handleDeleteFolder(e, folder.id)}>
                   <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </span>
              </div>
              <div className="folder-content">
                {folderMap[folder.id]?.length === 0 ? (
                  <div className="sidebar-empty" style={{ padding: '4px', fontStyle: 'italic', fontSize: '0.7rem' }}>Drop chats here</div>
                ) : (
                  folderMap[folder.id]?.map(renderSessionItem)
                )}
              </div>
            </div>
          ))}

          {isLoading && sessions.length === 0 ? (
            <div className="sidebar-loading">Loading...</div>
          ) : sessions.length === 0 && folders.length === 0 ? (
            <div className="sidebar-empty">No past sessions</div>
          ) : (
            Object.entries(groupedSessions).map(([groupName, gs]) => {
              if (gs.length === 0) return null;
              return (
                <div key={groupName} className="sidebar-group">
                  <div className="sidebar-group-title">{groupName}</div>
                  {gs.map(renderSessionItem)}
                </div>
              );
            })
          )}
        </div>
      </aside>
    </>
  );
}
