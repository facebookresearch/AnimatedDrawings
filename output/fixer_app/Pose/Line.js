//  Copyright (c) Meta Platforms, Inc. and affiliates.
//  This source code is licensed under the MIT license found in the
//  LICENSE file in the root directory of this source tree.

const Line = ({ isActive, ...props }) => {
  return (
    <>
      <line strokeWidth="4" stroke={isActive ? "black" : "white"} {...props} />
      <line strokeWidth="2" stroke={isActive ? "red" : "black"} {...props} />
    </>
  );
};

export default Line;
