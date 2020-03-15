import request from '@/utils/request';


//获取task任务列表
export async function gettasklist(params) {
  return request('/server/scantask/tasklist', {
    method: 'POST',
    data: { ...params, method: 'gettasklist' },
  });
}

//根据task id获取扫描结果列表
export function getscanlist(id,status) {
  console.log('id-id', id);
  return request('/server/scanlist/list', {
    method: 'POST',
    data: {id:id, status:status,method: 'getscanlist' },
  });
}

//根据task id和scanlist id标记删除，标记为误报的结果
export function updatescanlist(taskid, scanlistid,status) {
  console.log('taskid', taskid);
  console.log('scanlistid', scanlistid);
  return request('/server/scanlist/deleteid', {
    method: 'POST',
    data:{taskid:taskid,scanlistid:scanlistid,status:status,method:'updatescanlist'},
  });
}

//根据id将所有未处理的条目标记为忽略
export function updateallignore(id, status) {
  console.log('id', id);
  console.log('status', status);
  return request('/server/scanlist/updateallignore', {
    method: 'POST',
    data: { id:id,status:status,method:'updateallignore'},
  });
}