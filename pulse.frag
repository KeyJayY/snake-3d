#version 120

uniform sampler2D texture1;
varying vec2 vTexCoord;
varying vec3 vNormal;
varying vec3 vPos;

void main() {
    vec3 lightPos = vec3(5.0, 10.0, 10.0); 
    vec3 lightDir = normalize(lightPos - vPos);
    
    float diff = max(dot(vNormal, lightDir), 0.0);
    
    float ambientStrength = 0.5; 
    vec3 ambient = ambientStrength * vec3(1.0, 1.0, 1.0);
    
    vec3 diffuse = diff * vec3(0.5, 0.5, 0.5);
    
    vec4 texColor = texture2D(texture1, vTexCoord);
    
    vec3 result = (ambient + diffuse) * texColor.rgb;
    
    gl_FragColor = vec4(result, texColor.a);
}