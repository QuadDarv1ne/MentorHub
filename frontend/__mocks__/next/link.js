/* eslint-disable @typescript-eslint/no-require-imports */
const React = require('react');

function MockLink({ children, ...props }) {
  return React.createElement('a', props, children);
}

module.exports = MockLink;
