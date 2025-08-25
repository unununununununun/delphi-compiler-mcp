unit uJsonRpcServer;

interface

uses
  System.SysUtils, System.Classes,
  IdContext, IdCustomTCPServer, IdTCPServer;

type
  TOnJsonRequest = reference to procedure(const AId: string; const AMethod: string; const AParams: string; var AResult: string; var AError: string);

  TJsonRpcServer = class(TComponent)
  private
    FTcp: TIdTCPServer;
    FOnRequest: TOnJsonRequest;
    FToken: string;
    procedure DoExecute(AContext: TIdContext);
  public
    constructor Create(AOwner: TComponent); override;
    destructor Destroy; override;
    procedure Start(Host: string; Port: Integer; const Token: string = '');
    procedure Stop;
    property OnRequest: TOnJsonRequest read FOnRequest write FOnRequest;
  end;

implementation

uses
  System.JSON;

constructor TJsonRpcServer.Create(AOwner: TComponent);
begin
  inherited;
  FTcp := TIdTCPServer.Create(Self);
  FTcp.OnExecute := DoExecute;
end;

destructor TJsonRpcServer.Destroy;
begin
  Stop;
  inherited;
end;

procedure TJsonRpcServer.Start(Host: string; Port: Integer; const Token: string);
begin
  FToken := Token;
  FTcp.DefaultPort := Port;
  FTcp.Active := True;
end;

procedure TJsonRpcServer.Stop;
begin
  FTcp.Active := False;
end;

procedure TJsonRpcServer.DoExecute(AContext: TIdContext);
var
  LLine: string;
  LJson, LResultObj: TJSONObject;
  LId, LMethod, LError, LParamsStr, LResultStr: string;
  LParams: TJSONValue;
  LToken: string;
begin
  LLine := AContext.Connection.IOHandler.ReadLn;
  if LLine = '' then Exit;
  LJson := TJSONObject.ParseJSONValue(LLine) as TJSONObject;
  try
    if LJson = nil then Exit;
    LId := LJson.GetValue<string>('id', '');
    LMethod := LJson.GetValue<string>('method', '');
    LParams := LJson.getValue('params');
    if Assigned(LParams) then LParamsStr := LParams.ToJSON else LParamsStr := '{}';

    if LMethod = 'auth/handshake' then
    begin
      LToken := TJSONObject.ParseJSONValue(LParamsStr).GetValue<string>('token', '');
      if (FToken <> '') and (LToken <> FToken) then
      begin
        LResultObj := TJSONObject.Create;
        try
          LResultObj.AddPair('jsonrpc', '2.0');
          LResultObj.AddPair('id', LId);
          LResultObj.AddPair('error', TJSONObject.Create.AddPair('code', -32000).AddPair('message', 'unauthorized'));
          AContext.Connection.IOHandler.WriteLn(LResultObj.ToJSON);
        finally
          LResultObj.Free;
        end;
        Exit;
      end;
      Exit; // no response for notification
    end;

    if Assigned(FOnRequest) then
      FOnRequest(LId, LMethod, LParamsStr, LResultStr, LError)
    else
      LError := 'not implemented';

    LResultObj := TJSONObject.Create;
    try
      LResultObj.AddPair('jsonrpc', '2.0');
      if LId <> '' then LResultObj.AddPair('id', LId);
      if LError <> '' then
        LResultObj.AddPair('error', TJSONObject.Create.AddPair('code', -32603).AddPair('message', LError))
      else
        LResultObj.AddPair('result', TJSONObject.ParseJSONValue(LResultStr) as TJSONValue);
      AContext.Connection.IOHandler.WriteLn(LResultObj.ToJSON);
    finally
      LResultObj.Free;
    end;
  finally
    LJson.Free;
  end;
end;

end.