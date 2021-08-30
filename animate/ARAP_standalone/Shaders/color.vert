#version 330 core
layout(location = 0) in vec3 pos;

out vec3 ourColor;

void main() {
    gl_Position = vec4(pos, 1.0);
    ourColor = vec3(0.0, 0.0, 0.0);
}
