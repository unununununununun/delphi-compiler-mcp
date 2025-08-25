unit uMcpDebuggerWizard;

interface

uses
  ToolsAPI, System.SysUtils, System.Classes, Generics.Collections, uJsonRpcServer;

type
  TMcpDebuggerWizard = class(TNotifierObject, IOTAWizard, IOTADebuggerNotifier)
  private
    FRpc: TJsonRpcServer;
    FBreakpoints: TDictionary<string, IOTABreakpoint>;
    FNotifierIndex: Integer;
    procedure HandleRequest(const AId, AMethod, AParams: string; var AResult, AError: string);
    function DebuggerServices: IOTADebuggerServices;
    function BreakpointServices: IOTABreakpointServices;
    function AddSourceBreakpoint(const AFile: string; ALine: Integer): string;
    function RemoveBreakpointInternal(const AFile: string; ALine: Integer; const AId: string): Boolean;
    procedure SendOutput(const AText: string);
    procedure SendStopped(const AReason: string; ThreadId: Integer);
  public
    constructor Create;
    destructor Destroy; override;
    // IOTAWizard
    function GetIDString: string;
    function GetName: string;
    function GetState: TWizardState;
    procedure Execute;
    // IOTADebuggerNotifier
    procedure ProcessCreated(const Process: IOTAProcess);
    procedure ProcessDestroyed(const Process: IOTAProcess);
    procedure BreakpointAdded(const Breakpoint: IOTABreakpoint);
    procedure BreakpointDeleted(const Breakpoint: IOTABreakpoint);
    procedure BreakpointChanged(const Breakpoint: IOTABreakpoint);
    procedure WatchListChanged;
    procedure DebuggerStateChange(const NewState: TOTAEditState);
    procedure LocationUpdated(const Thread: IOTAThread; const SourcePosition: IOTAAddress);
  end;

procedure Register;

implementation

uses
  System.JSON;

procedure Register;
begin
  RegisterPackageWizard(TMcpDebuggerWizard.Create);
end;

{ TMcpDebuggerWizard }

constructor TMcpDebuggerWizard.Create;
var
  LPort: Integer;
  LToken: string;
  DS: IOTADebuggerServices;
begin
  inherited Create;
  FRpc := TJsonRpcServer.Create(nil);
  FRpc.OnRequest := HandleRequest;
  FBreakpoints := TDictionary<string, IOTABreakpoint>.Create;
  LPort := StrToIntDef(GetEnvironmentVariable('RAD_PLUGIN_PORT'), 5645);
  LToken := GetEnvironmentVariable('RAD_PLUGIN_TOKEN');
  FRpc.Start('127.0.0.1', LPort, LToken);
  DS := DebuggerServices;
  if Assigned(DS) then
    FNotifierIndex := DS.AddNotifier(Self)
  else
    FNotifierIndex := -1;
end;

destructor TMcpDebuggerWizard.Destroy;
var
  DS: IOTADebuggerServices;
begin
  if FNotifierIndex >= 0 then
  begin
    DS := DebuggerServices;
    if Assigned(DS) then
      DS.RemoveNotifier(FNotifierIndex);
  end;
  FBreakpoints.Free;
  FRpc.Stop;
  FRpc.Free;
  inherited;
end;

procedure TMcpDebuggerWizard.Execute;
begin
  // no UI
end;

function TMcpDebuggerWizard.GetIDString: string;
begin
  Result := 'Delphi.MCP.Debugger.Wizard';
end;

function TMcpDebuggerWizard.GetName: string;
begin
  Result := 'Delphi MCP Debugger';
end;

function TMcpDebuggerWizard.GetState: TWizardState;
begin
  Result := [wsEnabled];
end;

function TMcpDebuggerWizard.DebuggerServices: IOTADebuggerServices;
begin
  Supports(BorlandIDEServices, IOTADebuggerServices, Result);
end;

function TMcpDebuggerWizard.BreakpointServices: IOTABreakpointServices;
begin
  Supports(BorlandIDEServices, IOTABreakpointServices, Result);
end;

procedure TMcpDebuggerWizard.SendOutput(const AText: string);
var
  P: TJSONObject;
begin
  P := TJSONObject.Create;
  try
    P.AddPair('category', 'stdout');
    P.AddPair('text', AText);
    FRpc.Notify('debug/output', P.ToJSON);
  finally
    P.Free;
  end;
end;

procedure TMcpDebuggerWizard.SendStopped(const AReason: string; ThreadId: Integer);
var
  P: TJSONObject;
begin
  P := TJSONObject.Create;
  try
    P.AddPair('reason', AReason);
    P.AddPair('threadId', TJSONNumber.Create(ThreadId));
    FRpc.Notify('debug/stopped', P.ToJSON);
  finally
    P.Free;
  end;
end;

function TMcpDebuggerWizard.AddSourceBreakpoint(const AFile: string; ALine: Integer): string;
var
  BS: IOTABreakpointServices;
  BP: IOTASourceBreakpoint;
  Key: string;
begin
  Result := '';
  BS := BreakpointServices;
  if not Assigned(BS) then Exit;
  // Примечание: создание исходного брейкпоинта в OTAPI может отличаться по версиям.
  // В большинстве версий поддерживается AddSourceBreakpoint(FileName, Line), возвращает IOTASourceBreakpoint.
  BP := BS.AddSourceBreakpoint(AFile, ALine, 0, '');
  if Assigned(BP) then
  begin
    Key := Format('%s:%d', [AFile, ALine]);
    FBreakpoints.AddOrSetValue(Key, BP as IOTABreakpoint);
    Result := Key; // используем ключ как id для MVP
  end;
end;

function TMcpDebuggerWizard.RemoveBreakpointInternal(const AFile: string; ALine: Integer; const AId: string): Boolean;
var
  BS: IOTABreakpointServices;
  Key: string;
  BP: IOTABreakpoint;
begin
  Result := False;
  BS := BreakpointServices;
  if not Assigned(BS) then Exit;
  if AId <> '' then
    Key := AId
  else
    Key := Format('%s:%d', [AFile, ALine]);
  if FBreakpoints.TryGetValue(Key, BP) then
  begin
    BS.DeleteBreakpoint(BP);
    FBreakpoints.Remove(Key);
    Result := True;
  end;
end;

procedure TMcpDebuggerWizard.HandleRequest(const AId, AMethod, AParams: string; var AResult, AError: string);
var
  Params: TJSONObject;
  DS: IOTADebuggerServices;
  FileName: string;
  LineNum: Integer;
  BpId: string;
begin
  Params := TJSONObject.ParseJSONValue(AParams) as TJSONObject;
  try
    DS := DebuggerServices;
    if AMethod = 'debug/run' then
    begin
      if Assigned(DS) then
      begin
        DS.Run;
        SendOutput('Run\n');
        AResult := '{"status":"running"}';
      end
      else
        AError := 'IOTADebuggerServices not available';
    end
    else if AMethod = 'debug/continue' then
    begin
      if Assigned(DS) then
      begin
        DS.Run;
        SendOutput('Continue\n');
        AResult := '{"status":"continued"}';
      end
      else
        AError := 'IOTADebuggerServices not available';
    end
    else if AMethod = 'debug/stepOver' then
    begin
      if Assigned(DS) then
      begin
        DS.StepOver;
        SendOutput('StepOver\n');
        AResult := '{"status":"stepped"}';
      end
      else
        AError := 'IOTADebuggerServices not available';
    end
    else if AMethod = 'debug/setBreakpoint' then
    begin
      if Assigned(Params) then
      begin
        FileName := Params.GetValue<string>('file', '');
        LineNum := Params.GetValue<Integer>('line', 0);
        BpId := AddSourceBreakpoint(FileName, LineNum);
        if BpId <> '' then
          AResult := Format('{"id":"%s","file":"%s","line":%d}', [BpId, FileName, LineNum])
        else
          AError := 'failed to add breakpoint';
      end
      else
        AError := 'params required';
    end
    else if AMethod = 'debug/removeBreakpoint' then
    begin
      FileName := '';
      LineNum := 0;
      if Assigned(Params) then
      begin
        if Params.TryGetValue<string>('file', FileName) then ;
        if Params.TryGetValue<Integer>('line', LineNum) then ;
        Params.TryGetValue<string>('id', BpId);
      end;
      if RemoveBreakpointInternal(FileName, LineNum, BpId) then
        AResult := '{"removed":true}'
      else
        AError := 'breakpoint not found';
    end
    else
      AError := 'unknown method';
  finally
    Params.Free;
  end;
end;

// IOTADebuggerNotifier

procedure TMcpDebuggerWizard.ProcessCreated(const Process: IOTAProcess);
begin
  SendOutput('process created\n');
end;

procedure TMcpDebuggerWizard.ProcessDestroyed(const Process: IOTAProcess);
begin
  FRpc.Notify('debug/exited', '{"exitCode":0}');
end;

procedure TMcpDebuggerWizard.BreakpointAdded(const Breakpoint: IOTABreakpoint);
begin
  // no-op
end;

procedure TMcpDebuggerWizard.BreakpointDeleted(const Breakpoint: IOTABreakpoint);
begin
  // no-op
end;

procedure TMcpDebuggerWizard.BreakpointChanged(const Breakpoint: IOTABreakpoint);
begin
  // no-op
end;

procedure TMcpDebuggerWizard.WatchListChanged;
begin
  // no-op
end;

procedure TMcpDebuggerWizard.DebuggerStateChange(const NewState: TOTAEditState);
begin
  // When paused on breakpoint, IDE switches state; emit stopped as heuristic
  SendStopped('breakpoint', 0);
end;

procedure TMcpDebuggerWizard.LocationUpdated(const Thread: IOTAThread; const SourcePosition: IOTAAddress);
begin
  // could emit finer-grained updates if needed
end;

end.