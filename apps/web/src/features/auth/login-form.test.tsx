/**
 * Regression test for the bug where filling in the login form and submitting
 * produced empty-field errors ("ایمیل را وارد کنید.") and never sent a request:
 * `TextField` rendered a bare `name` attribute without calling `register()`, so
 * react-hook-form validated the untouched `defaultValues`.
 *
 * The only thing stubbed is `fetch` (and `next/navigation`), so the assertion
 * runs through the real chain: TextField registration -> react-hook-form -> zod
 * resolver -> react-query mutation -> generated client -> customFetch. Typecheck,
 * lint and build all pass on an unregistered field, which is why this exists.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactElement } from 'react';

const replace = vi.fn();
const refresh = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace, refresh, push: vi.fn(), back: vi.fn(), prefetch: vi.fn() }),
}));

const { LoginForm } = await import('./login-form');

function renderWithQueryClient(ui: ReactElement) {
  // A per-test client with retries off: a failed mutation must surface at once
  // instead of being retried behind the assertion.
  const queryClient = new QueryClient({
    defaultOptions: { mutations: { retry: false }, queries: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => {
  fetchMock.mockReset();
  replace.mockReset();
  refresh.mockReset();
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('LoginForm', () => {
  it('submits the typed credentials instead of the empty defaults', async () => {
    const user = userEvent.setup();
    fetchMock.mockResolvedValue(
      jsonResponse(200, { data: { user: { id: 1, email: 'user@example.com' } } }),
    );

    renderWithQueryClient(<LoginForm />);

    await user.type(screen.getByLabelText('ایمیل'), 'user@example.com');
    await user.type(screen.getByLabelText('رمز عبور'), 'secret-password');
    await user.click(screen.getByRole('button', { name: 'ورود' }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    const [url, init] = fetchMock.mock.calls[0]!;
    expect(url).toBe('/api/v1/auth/login');
    expect(init?.method).toBe('POST');
    // The payload is what actually proves registration worked: an unregistered
    // field would never have reached the resolver, let alone the request body.
    expect(JSON.parse(String(init?.body))).toEqual({
      email: 'user@example.com',
      password: 'secret-password',
    });

    expect(screen.queryByText('ایمیل را وارد کنید.')).toBeNull();
    expect(screen.queryByText('رمز عبور را وارد کنید.')).toBeNull();

    await waitFor(() => {
      expect(replace).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('reports empty fields and sends nothing when the form is untouched', async () => {
    const user = userEvent.setup();

    renderWithQueryClient(<LoginForm />);
    await user.click(screen.getByRole('button', { name: 'ورود' }));

    expect(await screen.findByText('ایمیل را وارد کنید.')).toBeVisible();
    expect(screen.getByText('رمز عبور را وارد کنید.')).toBeVisible();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('marks the email invalid without asking for it again', async () => {
    const user = userEvent.setup();

    renderWithQueryClient(<LoginForm />);
    await user.type(screen.getByLabelText('ایمیل'), 'not-an-email');
    await user.type(screen.getByLabelText('رمز عبور'), 'secret-password');
    await user.click(screen.getByRole('button', { name: 'ورود' }));

    expect(await screen.findByText('قالب ایمیل معتبر نیست.')).toBeVisible();
    expect(screen.queryByText('ایمیل را وارد کنید.')).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('surfaces the backend message on rejected credentials', async () => {
    const user = userEvent.setup();
    fetchMock.mockResolvedValue(
      jsonResponse(401, {
        error: { code: 'invalid_credentials', message: 'ایمیل یا رمز عبور نادرست است.' },
      }),
    );

    renderWithQueryClient(<LoginForm />);
    await user.type(screen.getByLabelText('ایمیل'), 'user@example.com');
    await user.type(screen.getByLabelText('رمز عبور'), 'wrong-password');
    await user.click(screen.getByRole('button', { name: 'ورود' }));

    expect(await screen.findByText('ایمیل یا رمز عبور نادرست است.')).toBeVisible();
    expect(replace).not.toHaveBeenCalled();
  });
});
