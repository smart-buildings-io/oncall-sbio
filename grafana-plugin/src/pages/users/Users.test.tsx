import 'jest/matchMedia.ts';
import React from 'react';

import { render, screen } from '@testing-library/react';

import { Users } from './Users';
import { UserStore } from 'models/user/user';
import { RootStore } from 'state';
import { BrowserRouter } from 'react-router-dom';

jest.mock('utils/authorization', () => ({
  ...jest.requireActual('utils/authorization'),
  isUserActionAllowed: jest.fn().mockReturnValue(true),
}));

jest.mock('@grafana/runtime', () => ({
  config: {
    featureToggles: {
      topNav: false,
    },
  },

  locationService: {
    partial: jest.fn(),
    replace: jest.fn(),
    push: jest.fn(),
  },
  getBackendSrv: () => ({
    get: jest.fn(),
    post: jest.fn(),
  }),
}));

const locationMock = {
  pathName: 'a/grafana-oncall-app/users',
  search: '',
};

const matchMock = {
  isExact: true,
  params: {},
  path: 'a/grafana-oncall-app/users',
  url: 'a/grafana-oncall-app/users',
};

const queryMock = {
  p: 1,
};

const historyMock = {
  push: jest.fn(),
  location: locationMock,
};

let store;

const rootStore = new RootStore();

describe('Users', () => {
  beforeEach(() => {
    store = {
      userStore: new UserStore(rootStore),
    };
  });

  test("It renders user's profile", () => {
    render(
      <BrowserRouter>
        <Users
          history={historyMock as any}
          location={locationMock as any}
          match={matchMock as any}
          meta={locationMock as any}
          query={queryMock}
          store={store}
        />
      </BrowserRouter>
    );
    const userSettings = screen.queryByTestId<HTMLElement>('user-settings');
    expect(userSettings).toBeDefined();
  });
});
