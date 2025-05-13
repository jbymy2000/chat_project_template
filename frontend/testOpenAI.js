const OpenAI = require("openai");

const openai = new OpenAI({
    apiKey: "sk-WRw4oiycBCeO1EeY357eA94cE60e4eA7961fFb9bEd746fAe", 
    baseURL: "https://pro.aiskt.com/v1"
});

async function testConnection() {
    try {
        const completion = await openai.completions.create({
            model: "gpt-4o",
            prompt: "Say hello in one sentence.",
            max_tokens: 10
        });

        console.log("AI Response:", completion.choices[0].text.trim());
    } catch (error) {
        console.error("Error:", error);
    }
}

// 执行测试
testConnection();

