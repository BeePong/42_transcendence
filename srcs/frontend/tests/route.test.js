import fetchMock from 'jest-fetch-mock';
import { navigate, loadPage, updatePageContent, changeRedirectUrlandOauthState } from '../js/route';
import { openWebSocket } from '../js/websockets';

// Mock external dependencies
jest.mock('../js/websockets', () => ({
  openWebSocket: jest.fn()
}));

// Mock global functions
global.console.error = jest.fn();
global.history.pushState = jest.fn();

beforeEach(() => {
  fetchMock.resetMocks();
});

describe('Navigation Functions', () => {
  beforeEach(() => {
    // Clear mocks before each test
    jest.clearAllMocks();

    // Mock DOM elements
    document.body.innerHTML = `
      <div id="content"></div>
      <form id="login-form">
        <input type="hidden" id="redirectUrl" />
      </form>
      <a id="login-42-url" href="https://example.com/oauth"></a>
    `;
  });

  // describe('navigate', () => {
  //   test('should navigate to a new path and call loadPage', () => {
  //     const mockEvent = {
  //       preventDefault: jest.fn(),
  //       currentTarget: { getAttribute: () => '/new-path' }
  //     };

  //     // Mock loadPage to spy on it
  //     jest.spyOn(global, 'loadPage').mockImplementation(() => Promise.resolve());

  //     navigate(mockEvent);

  //     expect(mockEvent.preventDefault).toHaveBeenCalled();
  //     expect(loadPage).toHaveBeenCalledWith('/new-path', '/', true);
  //   });

  //   test('should not reload the page if navigating to the same path', () => {
  //     window.location.pathname = '/current-path';

  //     jest.spyOn(global, 'loadPage').mockImplementation(() => Promise.resolve());

  //     navigate('/current-path');

  //     expect(loadPage).not.toHaveBeenCalled();
  //   });
  // });

  describe('loadPage', () => {
    test('should fetch and update content for a valid path', async () => {
      const path = '/new-path';
      const queryString = 'test=123';
      const responseText = '<p>New content</p>';

      fetchMock.mockResponseOnce(responseText);

      await loadPage(path, '/', true, queryString);

      expect(fetchMock).toHaveBeenCalledWith(`/page${path}/${queryString}`);
      expect(document.getElementById('content').innerHTML).toBe(responseText);
      expect(global.history.pushState).toHaveBeenCalledWith(null, null, path);
    });

    // test('should handle 400 error by navigating to OAuth error page', async () => {
    //   fetchMock.mockResponseOnce('', { status: 400 });

    //   await loadPage('/some-path');

    //   expect(fetchMock).toHaveBeenCalledWith('/page/some-path/');
    //   expect(navigate).toHaveBeenCalledWith('/accounts/oauth_error/');
    // });

    // test('should handle 401 error by navigating to login page', async () => {
    //   fetchMock.mockResponseOnce('', { status: 401 });

    //   await loadPage('/some-path', '/redirect-url');

    //   expect(fetchMock).toHaveBeenCalledWith('/page/some-path/');
    //   expect(navigate).toHaveBeenCalledWith('/accounts/login/', '/redirect-url');
    // });

    test('should handle network error', async () => {
      fetchMock.mockRejectOnce(new Error('Network error'));

      await loadPage('/some-path');

      expect(fetchMock).toHaveBeenCalledWith('/page/some-path/');
      expect(console.error).toHaveBeenCalledWith('There was a problem with the fetch operation:', expect.any(Error));
    });
  });

  describe('updatePageContent', () => {
    test('should update the page content', () => {
      const pageData = '<h1>Updated Content</h1>';

      updatePageContent(pageData, '/home', '/');

      expect(document.getElementById('content').innerHTML).toBe(pageData);
    });

    test('should handle tournament lobby websocket', () => {
      const pageData = '<div>Tournament Lobby</div>';

      updatePageContent(pageData, '/tournament/123/lobby', '/');

      expect(openWebSocket).toHaveBeenCalledWith('123');
    });

    test('should handle solo game websocket', () => {
      const pageData = '<div>Solo Game</div>';

      updatePageContent(pageData, '/tournament/solo_game', '/');

      expect(openWebSocket).toHaveBeenCalledWith('solo');
    });
  });

  // describe('changeRedirectUrlandOauthState', () => {
  //   test('should update the redirect URL and OAuth state', () => {
  //     const redirectUrl = '/new-redirect';
  //     const currentPort = window.location.port || '8080';
  
  //     // Call the function to update URL and state
  //     changeRedirectUrlandOauthState(redirectUrl);
  
  //     // Get the updated elements and URLs
  //     const login42UrlElement = document.getElementById('login-42-url');
  //     const updatedLogin42Url = new URL(login42UrlElement.href);
  //     const expectedUrl = `https://localhost:${currentPort}${redirectUrl}`;
  //     const expectedState = `qwerty|${encodeURIComponent(expectedUrl)}`;
  
  //     expect(document.getElementById('redirectUrl').value).toBe(redirectUrl);
  //     expect(updatedLogin42Url.searchParams.get('state')).toBe(expectedState);
  //   });
  // });
});
