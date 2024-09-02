import { loadPage } from '../js/route';

describe('loadPage', () => {
  beforeEach(() => {
    // Clear mocks before each test
    fetch.resetMocks();
    jest.clearAllMocks();

    // Mock DOM elements
    document.body.innerHTML = '<div id="content"></div>';
    global.history.pushState = jest.fn();
    global.fetchOauthErrorPage = jest.fn();
    global.redirectToLoginPage = jest.fn();
    global.changeRedirectUrlandOauthState = jest.fn();
    global.tournamentLobbyCountdown = jest.fn();
    global.mockWebSocket = jest.fn();
  });

  test('should fetch and update content for a valid path', async () => {
    const path = '/new-path';
    const queryString = 'test=123';
    const responseText = '<p>New content</p>';

    // Mock fetch to resolve with dummy content
    fetch.mockResponseOnce(responseText);

    await loadPage(path, '/', true, queryString);

    expect(fetch).toHaveBeenCalledWith(`/page${path}/${queryString}`);
    expect(document.getElementById('content').innerHTML).toBe(responseText);
    expect(global.history.pushState).toHaveBeenCalledWith(null, null, path);
  });
});
