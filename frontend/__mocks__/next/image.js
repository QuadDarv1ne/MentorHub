module.exports = function MockImage(props) {
  const { src, alt, width, height, ...rest } = props;
  return require('react').createElement('img', { src, alt, width, height, ...rest });
};
