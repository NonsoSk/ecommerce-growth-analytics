"""Build a local-only Tableau copy from the user-verified revenue probe."""
from pathlib import Path
from copy import deepcopy
import csv, hashlib, json, uuid
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dashboard/workbooks/SYNTHETIC_Growth_BUILD.twb'
DOLLARS='c"$"#,##0.00'
PERCENT='p0.00%'
def sub(parent, tag, text=None, **attrs):
    x=E.SubElement(parent,tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
    if text is not None:x.text=text
    return x
def ident(parent,key):sub(parent,'simple-id',uuid='{'+str(uuid.uuid5(uuid.NAMESPACE_URL,key)).upper()+'}')
def column(name,caption,typ='integer',formula=None,fmt=None):
    x=E.Element('column',name=f'[{name}]',caption=caption,datatype=typ,role='dimension' if typ in ('string','date','boolean') else 'measure',type='nominal' if typ in ('string','boolean') else 'ordinal' if typ=='date' else 'quantitative')
    if fmt:x.set('default-format',fmt)
    if formula is not None:sub(x,'calculation',**{'class':'tableau','formula':formula})
    return x

def build():
    root=E.parse(ROOT/'dashboard/templates/workbook.twb').getroot()
    root.set('xmlns:user','http://www.tableausoftware.com/xml/user')
    cards_template=deepcopy(root.find('./windows/window/cards'))
    template=deepcopy(root.find('./worksheets/worksheet[@name="SYNTHETIC — Orders"]'))
    for tag in ('datasources','worksheets','windows','dashboards','thumbnails'):
        el=root.find(tag)
        if el is not None:root.remove(el)
    sources=sub(root,'datasources');sheets=sub(root,'worksheets');boards=sub(root,'dashboards');windows=sub(root,'windows',source_height='30')
    params=sub(sources,'datasource',name='Parameters',inline='true',version='18.1',hasconnection='false')
    param_specs={'Start':('Start date','date','2026-01-01',None),'End':('End date (inclusive)','date','2026-03-31',None),
      'Device':('Funnel device','string','All',['All','mobile','desktop']),
      'Traffic':('Funnel source','string','All',['All','google','meta','organic','direct']),
      'Visit':('Funnel observed visit cohort','string','All',['All','first_observed_visit','returning_visit']),
      'Paid':('Acquisition paid source','string','All',['All','google','meta']),
      'Campaign':('Acquisition campaign','string','All',['All','syn_google_prospecting','syn_google_retargeting','syn_meta_prospecting','syn_meta_retargeting'])}
    for key,(caption,typ,value,options) in param_specs.items():
        literal=f'#{value}#' if typ=='date' else f'"{value}"'
        c=column(key,caption,typ,literal);c.set('param-domain-type','list' if options else 'any');c.set('value',literal)
        if options:
            members=sub(c,'members')
            for v in options:sub(members,'member',value=f'"{v}"')
        params.append(c)
    dsmap={}; sheetmap={}; formulas={}
    for group in ('overview','funnel','acquisition'):
        rows=list(csv.DictReader((ROOT/f'dashboard/data/{group}.csv').open())); headers=list(rows[0])
        ds=sub(sources,'datasource',name='federated.'+group,caption='SYNTHETIC '+group,inline='true',version='18.1')
        dsmap[group]=ds
        conn=sub(ds,'connection',**{'class':'federated'});ncs=sub(conn,'named-connections');nc=sub(ncs,'named-connection',name='textscan.'+group,caption=group)
        sub(nc,'connection',**{'class':'textscan','directory':str(ROOT/'dashboard/data'),'filename':group+'.csv','password':'','server':''})
        rel=sub(conn,'relation',connection='textscan.'+group,name=group+'.csv',table=f'[{group}#csv]',type='table');cols=sub(rel,'columns',character_set='UTF-8',header='yes',locale='en',separator=',')
        objectid=group+'.csv_demo'
        meta=sub(conn,'metadata-records')
        for i,key in enumerate(headers):
            typ='date' if key=='day' else 'string' if key in ('device','channel','visit_type','campaign_id','coverage') else 'integer'
            sub(cols,'column',datatype=typ,name=key,ordinal=i)
            rec=sub(meta,'metadata-record',**{'class':'column'})
            for tag,val in [('remote-name',key),('remote-type',133 if typ=='date' else 129 if typ=='string' else 20),('local-name',f'[{key}]'),('parent-name',f'[{group}.csv]'),('remote-alias',key),('ordinal',i),('local-type',typ),('aggregation','Year' if typ=='date' else 'Count' if typ=='string' else 'Sum'),('contains-null','true'),('object-id',f'[{objectid}]')]:sub(rec,tag,str(val))
            ds.append(column(key,key.replace('_',' ').title(),typ))
        eligible='[day] >= [Parameters].[Start] AND [day] <= [Parameters].[End]'
        mapping={'funnel':{'Device':'device','Traffic':'channel','Visit':'visit_type'},'acquisition':{'Paid':'channel','Campaign':'campaign_id'}}.get(group,{})
        for param,field in mapping.items():eligible+=f' AND ([Parameters].[{param}] = "All" OR [{field}] = [Parameters].[{param}])'
        ds.append(column('Eligible','Eligible reporting rows','boolean',eligible))
        receipt=json.loads((OUT.parent/'extract_receipt.json').read_text())[group]
        assert hashlib.sha256((ROOT/f'dashboard/data/{group}.csv').read_bytes()).hexdigest()==receipt['csv_sha256']
        extract=sub(ds,'extract',count='-1',enabled='true',object_id='',units='records',user_specific='false')
        ec=sub(extract,'connection',**{'class':'hyper','dbname':receipt['path'],'schema':'Extract','tablename':'Extract','access_mode':'readonly','default-settings':'hyper','username':'tableau_internal_user'})
        sub(ec,'relation',name='Extract',table='[Extract].[Extract]',type='table')
        em=deepcopy(meta)
        for record in em:
            record.find('parent-name').text='[Extract]'
        ec.append(em)
        graph=sub(ds,'object-graph');objects=sub(graph,'objects');obj=sub(objects,'object',caption=group+'.csv',id=objectid);props=sub(obj,'properties',context='');props.append(deepcopy(rel))
        ep=sub(obj,'properties',context='extract');sub(ep,'relation',name='Extract',table='[Extract].[Extract]',type='table')
    def sheet(group,title,formula,fmt=None,dimension=None):
        ds=dsmap[group];key='Metric_'+str(len(sheetmap)+1); c=column(key,title,'real',formula,fmt)
        ds.insert(list(ds).index(ds.find('extract')),deepcopy(c));formulas[title]=formula
        name='SYNTHETIC — '+title;ws=deepcopy(template);ws.set('name',name);ws.remove(ws.find('simple-id'));ident(ws,name)
        view=ws.find('./table/view');view.clear();links=sub(view,'datasources')
        sub(links,'datasource',name=ds.get('name'),caption=ds.get('caption'));sub(links,'datasource',name='Parameters',caption='Parameters')
        pd=sub(view,'datasource-dependencies',datasource='Parameters')
        for pc in params:pd.append(deepcopy(pc))
        dep=sub(view,'datasource-dependencies',datasource=ds.get('name'))
        for dc in ds.findall('column'):dep.append(deepcopy(dc))
        inst=f'[usr:{key}:qk]';sub(dep,'column-instance',column=f'[{key}]',derivation='User',name=inst,pivot='key',type='quantitative')
        sub(dep,'column-instance',column='[Eligible]',derivation='None',name='[none:Eligible:nk]',pivot='key',type='nominal')
        if dimension:sub(dep,'column-instance',column=f'[{dimension}]',derivation='None',name=f'[none:{dimension}:nk]',pivot='key',type='nominal')
        filt=sub(view,'filter',**{'class':'categorical','column':f'[{ds.get("name")}].[none:Eligible:nk]'})
        sub(filt,'groupfilter',**{'function':'member','level':'[none:Eligible:nk]','member':'true'})
        sub(view,'aggregation',value='true')
        pane=ws.find('./table/panes/pane');pane.find('encodings/text').set('column',f'[{ds.get("name")}].{inst}')
        style=pane.find('style/style-rule');sub(style,'format',attr='font-size',value='12' if dimension else '20');sub(style,'format',attr='color',value='#17354a')
        if dimension:
            pane.find('mark').set('class','Bar')
            ws.find('./table/cols').text=f'[{ds.get("name")}].{inst}'
        ws.find('./table/rows').text=f'[{ds.get("name")}].[none:{dimension}:nk]' if dimension else None
        sheets.append(ws);win=sub(windows,'window',**{'class':'worksheet','name':name});win.append(deepcopy(cards_template));ident(win,name+'window')
        sheetmap[title]=name
        return name
    ov=[('Sessions','SUM([sessions])',None),('Converting sessions','SUM([converting_sessions])',None),('Purchase conversion','IF SUM([sessions]) > 0 THEN SUM([converting_sessions])/SUM([sessions]) END',PERCENT),('Orders','SUM([orders])',None),('Net merchandise revenue USD','SUM([net_revenue_cents])/100.0',DOLLARS),('Merchandise refunds USD','SUM([refunds_cents])/100.0',DOLLARS),('Advertising spend USD','IF SUM([missing_spend_days])=0 THEN SUM([spend_cents])/100.0 END',DOLLARS)]
    ovnames=[sheet('overview',*m) for m in ov]
    stages=[('01 Session starts','session_starts'),('02 Product views','product_views'),('03 Add to cart','carts'),('04 Checkout','checkouts'),('05 Ordered purchase','purchases')]
    fnames=[sheet('funnel',title,f'SUM([{field}])') for title,field in stages]
    for i in range(4):
        a,b=stages[i][1],stages[i+1][1]
        fnames.append(sheet('funnel',f'Drop-off {i+1} to {i+2}',f'SUM([{a}])-SUM([{b}])'))
    fextra=[sheet('funnel','Ordered conversion by '+dim,'IF SUM([sessions])>0 THEN SUM([purchases])/SUM([sessions]) END',PERCENT,dim) for dim in ('device','channel')]
    fextra.append(sheet('funnel','Skipped or out-of-order sessions','SUM([skipped_or_out_of_order_sessions])'))
    ac=[('Paid spend USD','IF SUM([missing_spend_days])=0 THEN SUM([spend_cents])/100.0 END',DOLLARS),('Paid-attributed net revenue USD','SUM([net_revenue_cents])/100.0',DOLLARS),('Paid-attributed orders','SUM([attributed_orders])',None),('Net attributed ROAS','IF SUM([missing_spend_days])=0 AND SUM([spend_cents])>0 THEN SUM([net_revenue_cents])/SUM([spend_cents]) END','n0.00'),('First-observed paid CAC proxy USD','IF SUM([missing_spend_days])=0 AND SUM([first_observed_purchasers])>0 THEN SUM([spend_cents])/100.0/SUM([first_observed_purchasers]) END',DOLLARS)]
    anames=[sheet('acquisition',*m) for m in ac]
    acomp=[sheet('acquisition','Campaign '+title,formula,fmt,'campaign_id') for title,formula,fmt in (ac[0],ac[1],ac[3],ac[4])]
    acomp.append(sheet('acquisition','Days with spend and zero attributed orders','SUM([days_with_spend_zero_orders])'))
    def dashboard(title,kpis,details,parameters,note,columns):
        name='SYNTHETIC — '+title;d=sub(boards,'dashboard',name=name);sub(d,'style');sub(d,'size',sizing_mode='fixed',minwidth='1400',maxwidth='1400',minheight='1000',maxheight='1000')
        links=sub(d,'datasources');sub(links,'datasource',name='Parameters',caption='Parameters');dep=sub(d,'datasource-dependencies',datasource='Parameters')
        for c in params:dep.append(deepcopy(c))
        zones=sub(d,'zones');idx=0
        def zone(x,y,w,h,**attrs):
            nonlocal idx
            idx+=1;return sub(zones,'zone',id=idx,x=x,y=y,w=w,h=h,**attrs)
        z=zone(1500,1000,97000,5500,type_v2='text');ft=sub(z,'formatted-text');sub(ft,'run','SYNTHETIC DEMONSTRATION | '+title,bold='true',fontsize='22')
        z=zone(1500,6500,97000,8000,type_v2='text');ft=sub(z,'formatted-text');sub(ft,'run','Available data: Jan 1–Mar 31, 2026 UTC. Selected period: date controls below. USD • Refund observation cutoff Apr 16, 2026 (exclusive). '+note,fontsize='10')
        for i,param in enumerate(parameters):zone(1500+i*int(97000/len(parameters)),15000,int(95000/len(parameters)),7500,type_v2='paramctrl',param=f'[Parameters].[{param}]')
        for i,sname in enumerate(kpis):zone(1500+(i%columns)*int(97000/columns),24500+(i//columns)*14500,int(95000/columns),13500,name=sname,show_title='true')
        y=24500+((len(kpis)+columns-1)//columns)*14500
        for i,sname in enumerate(details):zone(1500+(i%2)*48500,y+(i//2)*17000,47000,16000,name=sname,show_title='true')
        ident(d,name);w=sub(windows,'window',**{'class':'dashboard','name':name});vp=sub(w,'viewpoints')
        for sname in kpis+details:
            v=sub(vp,'viewpoint',name=sname);sub(v,'zoom',type='entire-view')
        sub(w,'active',id='1');ident(w,name+'window')
        return w
    w=dashboard('Overview',ovnames,[],['Start','End'],'Distinct buying sessions / sessions; orders remain separate. Refunds assigned to originating session cohort. Date filters only. No real retailer findings.',4);w.set('maximized','true')
    dashboard('Funnel',fnames,fextra,['Start','End','Device','Traffic','Visit'],'Chronological, same-session journey; one session per eligible stage. Observed visit identity is not lifetime customer status. Comparisons are descriptive, not causal.',5)
    dashboard('Acquisition',anames,acomp,['Start','End','Paid','Campaign'],'Same-session campaign attribution, not incrementality. CAC uses first-observed purchasers, not proven new customers. Direct may include missing attribution/prior paid exposure; organic is not cost-free. Null ratio = zero denominator or missing spend.',5)
    names=[s.get('name') for s in sheets];assert len(names)==len(set(names))
    for ds in dsmap.values():
        names=[c.get('name') for c in ds.findall('column')];assert len(names)==len(set(names))
        assert all(list(ds).index(c)<list(ds).index(ds.find('extract')) for c in ds.findall('column'))
    sub(root,'thumbnails')
    E.indent(root);OUT.parent.mkdir(exist_ok=True)
    if OUT.exists():
        previous=OUT.read_bytes();backup=OUT.parent/'backups'/('DASHBOARDS_'+hashlib.sha256(previous).hexdigest()[:12]+'.twb')
        backup.parent.mkdir(exist_ok=True)
        if not backup.exists():backup.write_bytes(previous)
    E.ElementTree(root).write(OUT,encoding='utf-8',xml_declaration=True)
    evidence={'status':'generated_not_visually_validated','template_sha256':hashlib.sha256((ROOT/'dashboard/templates/workbook.twb').read_bytes()).hexdigest(),'workbook_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'worksheets':len(sheetmap),'dashboards':3,'formulas':formulas,'parameter_scopes':{'Start/End':'all','Device/Traffic/Visit':'funnel only','Paid/Campaign':'acquisition only'}}
    (OUT.parent/'build_manifest.json').write_text(json.dumps(evidence,indent=2))
    print(OUT);print(f'{len(sheetmap)} worksheets; 3 dashboards; sanitized template; no original draft dependency')
if __name__=='__main__':build()
