module.exports = function MockLink({ children, ...props }) {
  return require('react').createElement('a', props, children);
};
