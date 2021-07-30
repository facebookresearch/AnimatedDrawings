// Button.stories.ts | Button.stories.tsx

import React from "react";

import { Meta, Story } from "@storybook/react";
import PoseModal, { Props } from "./PoseStep";

export default {
  title: "Components/PoseModal",
  component: PoseModal,
} as Meta;

// export const Primary: React.VFC<{}> = () => <PoseModal uuid=""></PoseModal>;

//👇 We create a “template” of how args map to rendering
const Template: Story<Props> = (args) => <PoseModal {...args} />;

export const Primary = Template.bind({});

Primary.args = {
  uuid: "df12dbe4b1064bd9a614f66edba8d80e",
};
