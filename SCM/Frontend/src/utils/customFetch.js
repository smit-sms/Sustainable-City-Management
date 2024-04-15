import Cookies from "js-cookie";
import { BASE_URL } from '../services/api';

async function CustomFetch(url, options = {}, navigate) {
  options.headers = {
    ...options.headers,
    'Content-Type': 'application/json'
  };

  const accessToken = Cookies.get('access_token');
  if (accessToken) {
    options.headers['Authorization'] = `Bearer ${accessToken}`;
  }

  let response = await fetch(url, options);

  if (response.status === 401) {
    const refreshToken = Cookies.get('refresh_token');
    console.log("REFRESH TOKEN", refreshToken);
    const refreshResponse = await fetch(`${BASE_URL}/auth/token/refresh/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({refresh: refreshToken}),
    });

    if (refreshResponse.ok) {
      const data = await refreshResponse.json();
      Cookies.set('access_token', data.access);
      Cookies.set('refresh_token', data.refresh);

      // Retry the original request with the new access token
      options.headers['Authorization'] = `Bearer ${data.access}`;
      response = await fetch(url, options);
    } else {
      // Handle the case where refresh also fails
      navigate('/');
      throw new Error('Unable to refresh token');
    }
  }
  return response;
}

export default CustomFetch;
