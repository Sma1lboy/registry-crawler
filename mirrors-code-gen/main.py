from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# Initialize the OpenAI LLM
llm = OpenAI(api_key="your-openai-api-key")  # 替换为你的 OpenAI API 密钥

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["tool_name", "env_vars"],
    template="""
package source

import (
    "fmt"
    "os"
    "os/exec"
    "strings"
)

type {tool_name}RegistryManager struct{{}}

// GetCurrRegistry 获取当前 {tool_name} 环境变量配置
func (h {tool_name}RegistryManager) GetCurrRegistry() (map[string]string, error) {{
    envVars := []string{{
        {env_vars}
    }}
    registry := make(map[string]string)

    for _, env := range envVars {{
        value := os.Getenv(env)
        if value == "" {{
            continue
        }}
        registry[env] = value
    }}

    return registry, nil
}}

// SetRegistry 设置 {tool_name} 环境变量
func (h {tool_name}RegistryManager) SetRegistry(envs map[string]string) error {{
    for key, value := range envs {{
        err := exec.Command("sh", "-c", fmt.Sprintf("export %s=%s", key, value)).Run()
        if err != nil {{
            return err
        }}
    }}

    // 将环境变量写入到 shell 配置文件中
    homeDir, err := os.UserHomeDir()
    if err != nil {{
        return err
    }}

    shellConfigFiles := []string{{
        ".bash_profile",
        ".profile",
        ".zprofile",
    }}

    for _, configFile := range shellConfigFiles {{
        filePath := fmt.Sprintf("%s/%s", homeDir, configFile)
        for key, value := range envs {{
            cmd := exec.Command("sh", "-c", fmt.Sprintf("echo 'export %s=%s' >> %s", key, value, filePath))
            err := cmd.Run()
            if err != nil {{
                return err
            }}
        }}
    }}

    return nil
}}
""",
)


# Function to generate the code
def generate_code(tool_name, env_vars):
    env_vars_str = ", ".join([f'"{var}"' for var in env_vars])
    filled_prompt = prompt_template.format(tool_name=tool_name, env_vars=env_vars_str)
    response = llm(filled_prompt)
    return response["text"]


# Example usage
tool_name = "GenericTool"  # 这是一个通用的工具名称
env_vars = [
    "GENERIC_TOOL_API_DOMAIN",
    "GENERIC_TOOL_BOTTLE_DOMAIN",
    "GENERIC_TOOL_BREW_GIT_REMOTE",
    "GENERIC_TOOL_CORE_GIT_REMOTE",
]

code = generate_code(tool_name, env_vars)
print(code)
