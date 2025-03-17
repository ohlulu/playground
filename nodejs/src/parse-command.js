import parser from 'yargs-parser';

const input = "deploy -r slpos -e staging, preivew -m 'test message'"
const opt = {
    array: ['e'],
}
const argv = parser(input, opt)
console.log(argv)
console.log(argv._)

const a = "```\n" +
          "deploy [options]\n\n" +
          "Options:\n" +
          "  -r:  Release type (e.g., hotfix, feature)       [required]\n" +
          "  -e:  Environment(s) to deploy to                [required] [array]\n" +
          "  -b:  Branch name to deploy                      [required]\n" +
          "  -m:  Deployment message/description             [optional]\n" +
          "  -h:  Show this help message\n\n" +
          "Examples:\n" +
          "  deploy -r hotfix -e staging -b fix/login-issue\n" +
          "  deploy -r feature -e staging -e app-store -b feature/new-payment -m New payment feature deployment\n" +
          "```"

console.log(a)