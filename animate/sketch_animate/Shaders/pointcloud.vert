#version 330 core
layout(location = 0) in vec3 pos;
layout(location = 1) in vec3 color;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

out vec3 ourColor;

flat out int vertex_id;

void main() {
    gl_Position = proj * view * model * vec4(pos, 1);

    vertex_id = gl_VertexID;

    ourColor = color;
}
