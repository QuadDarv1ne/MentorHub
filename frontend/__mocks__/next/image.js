/* eslint-disable @typescript-eslint/no-require-imports */
const React = require('react');

function MockImage(props) {
  const { src, alt, width, height, fill, ...rest } = props;
  const imgProps = { src, alt, width, height, ...rest };
  if (fill !== undefined) {
    imgProps['data-fill'] = 'true';
  }
  return React.createElement('img', imgProps);
}

module.exports = MockImage;
