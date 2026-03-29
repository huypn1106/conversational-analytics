/**
 * Get all user sessions
 * @returns {Promise<Array<{ session_id: string, title: string, created_at: number }>>}
 */
export async function getAllSessions() {
  const response = await fetch("/api/sessions");
  if (!response.ok) {
    throw new Error(`Failed to fetch sessions: ${response.status}`);
  }
  return response.json();
}

export async function deleteSession(sessionId) {
  const response = await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
  if (!response.ok) throw new Error("Delete failed");
  return response.json();
}

export async function updateSessionFolder(sessionId, folderId) {
  const response = await fetch(`/api/sessions/${sessionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ folder_id: folderId })
  });
  if (!response.ok) throw new Error("Update failed");
  return response.json();
}

export async function getAllFolders() {
  const response = await fetch(`/api/folders`);
  if (!response.ok) throw new Error("Fetch failed");
  return response.json();
}

export async function createFolder(name) {
  const response = await fetch(`/api/folders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });
  if (!response.ok) throw new Error("Create failed");
  return response.json();
}

export async function deleteFolder(folderId, deleteConversations = false) {
  const response = await fetch(`/api/folders/${folderId}?delete_conversations=${deleteConversations}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error("Delete failed");
  return response.json();
}
