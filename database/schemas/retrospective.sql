-- retrospectives 테이블 생성
create table if not exists retrospectives (
    id bigint primary key generated always as identity,
    user_id text not null,
    session_name text not null,
    slack_channel text not null,
    slack_ts text not null,
    good_points text not null,
    improvements text not null,
    learnings text not null,
    action_item text not null,
    emotion_score integer check (emotion_score between 1 and 10 or emotion_score is null),
    emotion_reason text null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) null
); 

-- 업데이트 트리거 생성 (updated_at 자동 갱신)
create or replace function update_modified_column()
returns trigger as $$
begin
    new.updated_at = timezone('utc'::text, now());
    return new;
end;
$$ language 'plpgsql';

-- 트리거 설정
create trigger update_retrospectives_updated_at
before update on retrospectives
for each row
execute procedure update_modified_column(); 