/* eslint-disable @typescript-eslint/no-require-imports */
const React = require('react');

function MockImage(props) {
  const { src, alt, width, height, ...rest } = props;
  return React.createElement('img', { src, alt, width, height, ...rest });
}

module.exports = MockImage;
