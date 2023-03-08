const Line = ({ isActive, ...props }) => {
  return (
    <>
      <line strokeWidth="4" stroke={isActive ? "black" : "white"} {...props} />
      <line strokeWidth="2" stroke={isActive ? "red" : "black"} {...props} />
    </>
  );
};

export default Line;
