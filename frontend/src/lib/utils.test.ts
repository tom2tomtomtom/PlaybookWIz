import { slugify, isValidEmail, formatFileSize } from './utils';

describe('utils', () => {
  test('slugify converts strings to URL-friendly slugs', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  test('isValidEmail validates email addresses', () => {
    expect(isValidEmail('test@example.com')).toBe(true);
    expect(isValidEmail('invalid-email')).toBe(false);
  });

  test('formatFileSize formats bytes to human readable', () => {
    expect(formatFileSize(1024)).toBe('1 KB');
  });
});
