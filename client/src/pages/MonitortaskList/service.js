import request from '@/utils/request';
export async function queryRule(params) {
  return request('/api/task', {
    params,
  });
}
export async function removeRule(params) {
  console.log('removeRule', params);
  return request('/api/task', {
    method: 'POST',
    data: { ...params, method: 'remove' },
  });
}
export async function addRule(params) {
  return request('/api/task', {
    method: 'POST',
    data: { ...params, method: 'post' },
  });
}
export async function updateRule(params) {
  return request('/api/task', {
    method: 'POST',
    data: { ...params, method: 'update' },
  });
}

export async function deleteRule(params) {
  console.log('deleteRule', params);
  return request('/api/task', {
    method: 'POST',
    data: { ...params, method:'delete'},
  });
}
