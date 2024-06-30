export const refreshToken = async (refreshToken: string) => {
  const API_URL = process.env.API_URL;

  const res = await fetch(`${API_URL}/api/token/refresh/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "cache-control": "no-cache",
    },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  const data = await res.json();

  if (!res.ok) {
    return;
  }

  return data;
};
