#version 120

uniform float time;
varying vec2 vTexCoord;
varying vec3 vNormal;
varying vec3 vPos;

void main() {
    float scale = 1.0 + 0.15 * sin(time * 4.0); 
    vec4 vertex = gl_Vertex;
    vertex.xyz *= scale;

    vTexCoord = gl_MultiTexCoord0.xy;
    vNormal = normalize(gl_NormalMatrix * gl_Normal);
    
    vPos = vec3(gl_ModelViewMatrix * vertex);

    gl_Position = gl_ModelViewProjectionMatrix * vertex;
}