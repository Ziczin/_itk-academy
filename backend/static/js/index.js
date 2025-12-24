import Query from "./make_query.js"

const walletInput = document.getElementById('wallet');
const amountInput = document.getElementById('amount');
const urlInput = document.getElementById('url');
const codeResponse = document.getElementById('codeResponse');
const requestOutput = document.getElementById('requestOutput');
const responseOutput = document.getElementById('responseOutput');
const accountsList = document.getElementById('accountsList');
const getListBtn = document.getElementById('getListBtn');
const createBtn = document.getElementById('createBtn');
const getBalanceBtn = document.getElementById('getBalanceBtn');
const operationBtn = document.getElementById('operationBtn');
const operationTypeSelect = document.getElementById('operationType');

const colorMap = {
  '2': { 
    bg: 'var(--code-success-bg)', 
    color: 'var(--code-success-color)', 
  },
  '3': { 
    bg: 'var(--code-redirect-bg)', 
    color: 'var(--code-redirect-color)', 
  },
  '4': { 
    bg: 'var(--code-client-error-bg)', 
    color: 'var(--code-client-error-color)', 
  },
  '5': { 
    bg: 'var(--code-server-error-bg)', 
    color: 'var(--code-server-error-color)', 
  }
};

function setCodeColor(statusCode) {
  const codeStr = String(statusCode);
  const firstDigit = codeStr.charAt(0);
  const color = colorMap[firstDigit] || colorMap['2'];
  
  codeResponse.style.background = color.bg;
  codeResponse.style.color = color.color;
  codeResponse.textContent = `Код: ${statusCode}`;
}

function formatJson(data) {
  return JSON.stringify(data, null, 2);
}

const baseQuery = Query.new(['api', 'v1', 'wallets']);

async function executeQueryAndShowData(method, queryInstance) {
  const result = await queryInstance.fetch(method, true);
  
  setCodeColor(result.status);
  requestOutput.textContent = formatJson(queryInstance.q_body);
  responseOutput.textContent = formatJson(result.data);
  urlInput.value = queryInstance.q_url.split(': ')[1];
  
  return result.data;
}

function getBalance() {
  const query = baseQuery.view().at(walletInput.value);
  executeQueryAndShowData('GET', query);
}

function performOperation() {
  const query = baseQuery.view()
    .at(walletInput.value)
    .at('operation')
    .with({
      operation_type: operationTypeSelect.value,
      amount: parseFloat(amountInput.value)
    });
  
  executeQueryAndShowData('POST', query);
}

function createAccount() {
  const query = baseQuery.view();
  executeQueryAndShowData('POST', query);
}

async function getAccountList() {
  const data = await executeQueryAndShowData('GET', baseQuery.view());
  
  accountsList.innerHTML = '';
  
  if (data && Array.isArray(data)) {
    data.forEach(wallet => {
      const item = document.createElement('div');
      item.className = 'account-item';
      item.textContent = `${wallet.wallet_id} - ${wallet.balance} 'денег'`;
      item.addEventListener('click', () => {
        walletInput.value = wallet.wallet_id;
        amountInput.value = wallet.balance;
      });
      accountsList.appendChild(item);
    });
  }
}

getBalanceBtn.addEventListener('click', getBalance);
operationBtn.addEventListener('click', performOperation);
createBtn.addEventListener('click', createAccount);
getListBtn.addEventListener('click', getAccountList);

setCodeColor(200);
getAccountList();

export { getBalance, performOperation, setCodeColor, createAccount, getAccountList };